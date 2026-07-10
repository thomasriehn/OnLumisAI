"""Transaktionaler Upsert in die Wissensbasis + Tombstones (AP 1.4/1.5, §7.2).

Alte Chunks eines Dokuments werden in derselben Transaktion ersetzt, in der
das Dokument aktualisiert wird – die Suche sieht nie einen halben Zustand.
"""

import json
from dataclasses import dataclass
from uuid import UUID

import asyncpg

from .chunking import Chunk


def to_pgvector(vec: list[float]) -> str:
    return "[" + ",".join(f"{x:.7g}" for x in vec) + "]"


@dataclass
class ExistingDocument:
    content_hash: str
    meta: dict


async def load_document_index(
    conn: asyncpg.Connection, source_id: UUID
) -> dict[str, ExistingDocument]:
    rows = await conn.fetch(
        """
        SELECT external_id, content_hash, meta::text AS meta
        FROM knowledge.documents
        WHERE source_id = $1 AND deleted_at IS NULL
        """,
        source_id,
    )
    return {
        r["external_id"]: ExistingDocument(
            content_hash=r["content_hash"], meta=json.loads(r["meta"])
        )
        for r in rows
    }


async def upsert_document(
    conn: asyncpg.Connection,
    *,
    source_id: UUID,
    external_id: str,
    uri: str,
    title: str | None,
    mime_type: str | None,
    content_hash: str,
    acl_groups: list[str],
    meta: dict,
    chunks: list[Chunk],
    embeddings: list[list[float]],
) -> UUID:
    if len(chunks) != len(embeddings):
        raise ValueError("chunks und embeddings müssen gleich lang sein")
    async with conn.transaction():
        document_id = await conn.fetchval(
            """
            INSERT INTO knowledge.documents
                (source_id, external_id, uri, title, mime_type, content_hash,
                 acl_groups, meta)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
            ON CONFLICT (source_id, external_id) DO UPDATE SET
                uri          = EXCLUDED.uri,
                title        = EXCLUDED.title,
                mime_type    = EXCLUDED.mime_type,
                content_hash = EXCLUDED.content_hash,
                acl_groups   = EXCLUDED.acl_groups,
                meta         = EXCLUDED.meta,
                updated_at   = now(),
                deleted_at   = NULL
            RETURNING id
            """,
            source_id,
            external_id,
            uri,
            title,
            mime_type,
            content_hash,
            acl_groups,
            json.dumps(meta),
        )
        await conn.execute(
            "DELETE FROM knowledge.chunks WHERE document_id = $1", document_id
        )
        await conn.executemany(
            """
            INSERT INTO knowledge.chunks
                (document_id, chunk_index, content, heading_path, page, embedding)
            VALUES ($1, $2, $3, $4, $5, $6::vector)
            """,
            [
                (document_id, c.index, c.content, c.heading_path, c.page, to_pgvector(e))
                for c, e in zip(chunks, embeddings, strict=True)
            ],
        )
    return document_id


async def touch_document_meta(
    conn: asyncpg.Connection, source_id: UUID, external_id: str, meta: dict
) -> None:
    """Datei unverändert (gleicher Hash), aber mtime/size neu -> nur Meta pflegen."""
    await conn.execute(
        """
        UPDATE knowledge.documents SET meta = $3::jsonb, updated_at = now()
        WHERE source_id = $1 AND external_id = $2
        """,
        source_id,
        external_id,
        json.dumps(meta),
    )


async def tombstone_missing(
    conn: asyncpg.Connection, source_id: UUID, seen_external_ids: list[str]
) -> int:
    """Markiert in der Quelle verschwundene Dokumente und entfernt ihre Chunks
    (DSGVO-Löschkonzept, §7.2). Die Dokumentzeile bleibt als Tombstone."""
    async with conn.transaction():
        rows = await conn.fetch(
            """
            UPDATE knowledge.documents SET deleted_at = now()
            WHERE source_id = $1 AND deleted_at IS NULL
              AND NOT (external_id = ANY($2::text[]))
            RETURNING id
            """,
            source_id,
            seen_external_ids,
        )
        if rows:
            await conn.execute(
                "DELETE FROM knowledge.chunks WHERE document_id = ANY($1::uuid[])",
                [r["id"] for r in rows],
            )
    return len(rows)


async def set_sync_status(
    conn: asyncpg.Connection, source_id: UUID, status: str
) -> None:
    await conn.execute(
        """
        UPDATE knowledge.sources
        SET last_sync_at = now(), last_sync_status = $2
        WHERE id = $1
        """,
        source_id,
        status,
    )
