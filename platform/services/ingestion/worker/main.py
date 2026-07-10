"""Sync-Runner (AP 1.5): synchronisiert alle aktiven Quellen mit der Wissensbasis.

Betriebsmodi:
    python -m worker.main once          einmaliger Sync aller Quellen
    python -m worker.main loop          Dauerbetrieb (SYNC_INTERVAL_SECONDS)
    python -m worker.main add-source --name NAME --root PFAD [--acl g1,g2]

v1 arbeitet als sequentieller Scheduler; die Redis-Jobqueue aus AP 1.5 folgt,
sobald mehrere Konnektoren parallel laufen (Phase 3).
"""

import argparse
import asyncio
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

import asyncpg
import httpx

from . import indexer
from .chunking import chunk_blocks
from .config import settings
from .connectors.filesystem import FilesystemConnector
from .embedder import Embedder
from .parsing import parse_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("onlumis.ingestion")


@dataclass
class SyncStats:
    scanned: int = 0
    indexed: int = 0
    unchanged: int = 0
    removed: int = 0
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "ok" if not self.errors else f"error: {'; '.join(self.errors[:3])}"
        return (
            f"{status} (gescannt={self.scanned}, indexiert={self.indexed}, "
            f"unverändert={self.unchanged}, entfernt={self.removed})"
        )


async def sync_filesystem_source(
    pool: asyncpg.Pool, embedder: Embedder, source: asyncpg.Record
) -> SyncStats:
    stats = SyncStats()
    source_id: UUID = source["id"]
    config = json.loads(source["config"])
    acl_groups = list(source["default_acl"])
    connector = FilesystemConnector(Path(config["root_path"]))

    async with pool.acquire() as conn:
        existing = await indexer.load_document_index(conn, source_id)

    seen: list[str] = []
    for f in connector.scan():
        stats.scanned += 1
        seen.append(f.external_id)
        prev = existing.get(f.external_id)

        # Stufe 1: mtime/size unverändert -> Datei sicher unverändert
        if prev and prev.meta.get("mtime") == f.mtime and prev.meta.get("size") == f.size:
            stats.unchanged += 1
            continue

        try:
            digest = connector.content_hash(f.path)
            # Stufe 2: Inhalt unverändert (z. B. nur mtime durch Kopieren neu)
            if prev and prev.content_hash == digest:
                async with pool.acquire() as conn:
                    await indexer.touch_document_meta(conn, source_id, f.external_id, f.meta)
                stats.unchanged += 1
                continue

            parsed = parse_file(f.path)
            chunks = chunk_blocks(parsed.blocks)
            if not chunks:
                logger.warning("Kein extrahierbarer Text: %s (Scan ohne OCR?)", f.external_id)
                stats.errors.append(f"{f.external_id}: kein Text")
                continue

            embeddings = await embedder.embed([c.content for c in chunks])
            async with pool.acquire() as conn:
                await indexer.upsert_document(
                    conn,
                    source_id=source_id,
                    external_id=f.external_id,
                    uri=f.uri,
                    title=parsed.title or f.path.stem,
                    mime_type=f.mime_type,
                    content_hash=digest,
                    acl_groups=acl_groups,
                    meta=f.meta,
                    chunks=chunks,
                    embeddings=embeddings,
                )
            stats.indexed += 1
            logger.info("Indexiert: %s (%d Chunks)", f.external_id, len(chunks))
        except Exception as exc:  # noqa: BLE001 - eine Datei darf den Sync nicht stoppen
            logger.exception("Fehler bei %s", f.external_id)
            stats.errors.append(f"{f.external_id}: {exc}")

    async with pool.acquire() as conn:
        stats.removed = await indexer.tombstone_missing(conn, source_id, seen)
        await indexer.set_sync_status(conn, source_id, stats.summary())
    return stats


async def run_once(pool: asyncpg.Pool, embedder: Embedder) -> None:
    async with pool.acquire() as conn:
        sources = await conn.fetch(
            """
            SELECT id, name, kind, config::text AS config, default_acl
            FROM knowledge.sources
            WHERE enabled AND kind = 'filesystem'
            ORDER BY created_at
            """
        )
    if not sources:
        logger.info("Keine aktiven Quellen konfiguriert (add-source verwenden)")
        return
    for source in sources:
        logger.info("Sync von Quelle '%s' startet", source["name"])
        try:
            stats = await sync_filesystem_source(pool, embedder, source)
            logger.info("Quelle '%s': %s", source["name"], stats.summary())
        except Exception as exc:  # noqa: BLE001 - eine Quelle darf andere nicht stoppen
            logger.exception("Sync von '%s' fehlgeschlagen", source["name"])
            async with pool.acquire() as conn:
                await indexer.set_sync_status(conn, source["id"], f"error: {exc}")


async def run_loop(pool: asyncpg.Pool, embedder: Embedder) -> None:
    logger.info("Sync-Loop, Intervall %ss", settings.sync_interval_seconds)
    while True:
        await run_once(pool, embedder)
        await asyncio.sleep(settings.sync_interval_seconds)


async def add_source(pool: asyncpg.Pool, name: str, root: str, acl: list[str]) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO knowledge.sources (kind, name, config, default_acl)
            VALUES ('filesystem', $1, $2::jsonb, $3)
            ON CONFLICT (name) DO UPDATE
                SET config = EXCLUDED.config, default_acl = EXCLUDED.default_acl
            """,
            name,
            json.dumps({"root_path": root}),
            acl,
        )
    logger.info("Quelle '%s' angelegt/aktualisiert (root=%s, acl=%s)", name, root, acl)


async def amain(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="onlumis-ingestion")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("once")
    sub.add_parser("loop")
    p_add = sub.add_parser("add-source")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--root", required=True, help="Pfad innerhalb des Containers")
    p_add.add_argument("--acl", default="all-users", help="Kommagetrennte Gruppen")
    args = parser.parse_args(argv)

    pool = await asyncpg.create_pool(settings.database_url, min_size=1, max_size=5)
    try:
        if args.command == "add-source":
            acl = [g.strip() for g in args.acl.split(",") if g.strip()]
            await add_source(pool, args.name, args.root, acl)
            return 0
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as http:
            embedder = Embedder(http)
            if args.command == "once":
                await run_once(pool, embedder)
            else:
                await run_loop(pool, embedder)
        return 0
    finally:
        await pool.close()


def main() -> None:
    sys.exit(asyncio.run(amain(sys.argv[1:])))


if __name__ == "__main__":
    main()
