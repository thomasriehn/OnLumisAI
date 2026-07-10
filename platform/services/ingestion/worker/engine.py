"""Generische Sync-Engine für Remote-Konnektoren (AP 3.1, §7.2).

Change Detection über `RemoteDocument.version` (in documents.content_hash
gespeichert); Fehler einzelner Dokumente stoppen den Sync nicht.
"""

import logging
from dataclasses import dataclass, field
from uuid import UUID

import asyncpg

from . import indexer
from .chunking import chunk_blocks
from .connectors.base import RemoteConnector
from .embedder import Embedder

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


async def sync_remote_source(
    pool: asyncpg.Pool,
    embedder: Embedder,
    source: asyncpg.Record,
    connector: RemoteConnector,
) -> SyncStats:
    stats = SyncStats()
    source_id: UUID = source["id"]
    default_acl = list(source["default_acl"])

    async with pool.acquire() as conn:
        existing = await indexer.load_document_index(conn, source_id)

    seen: list[str] = []
    async for rd in connector.list_documents():
        stats.scanned += 1
        seen.append(rd.external_id)
        prev = existing.get(rd.external_id)
        if prev and prev.content_hash == rd.version:
            stats.unchanged += 1
            continue
        try:
            parsed = await connector.fetch(rd)
            chunks = chunk_blocks(parsed.blocks)
            if not chunks:
                logger.warning("Kein extrahierbarer Text: %s", rd.external_id)
                stats.errors.append(f"{rd.external_id}: kein Text")
                continue
            embeddings = await embedder.embed([c.content for c in chunks])
            async with pool.acquire() as conn:
                await indexer.upsert_document(
                    conn,
                    source_id=source_id,
                    external_id=rd.external_id,
                    uri=rd.uri,
                    title=parsed.title or rd.title,
                    mime_type=rd.mime_type,
                    content_hash=rd.version,
                    acl_groups=rd.acl_groups or default_acl,
                    meta=rd.meta,
                    chunks=chunks,
                    embeddings=embeddings,
                )
            stats.indexed += 1
            logger.info("Indexiert: %s (%d Chunks)", rd.external_id, len(chunks))
        except Exception as exc:  # noqa: BLE001 - ein Dokument stoppt den Sync nicht
            logger.exception("Fehler bei %s", rd.external_id)
            stats.errors.append(f"{rd.external_id}: {exc}")

    async with pool.acquire() as conn:
        stats.removed = await indexer.tombstone_missing(conn, source_id, seen)
        await indexer.set_sync_status(conn, source_id, stats.summary())
    return stats
