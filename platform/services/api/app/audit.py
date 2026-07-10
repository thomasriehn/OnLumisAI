"""Audit-Log (A7): append-only, Fragen wahlweise als Klartext oder SHA-256-Hash."""

import hashlib
import json
from uuid import UUID

import asyncpg

from .config import settings


async def log_event(
    conn: asyncpg.Connection,
    actor: str,
    action: str,
    *,
    question: str | None = None,
    document_ids: list[UUID] | None = None,
    chunk_ids: list[int] | None = None,
    conversation_id: UUID | None = None,
    model: str | None = None,
    meta: dict | None = None,
) -> None:
    question_plain = question if settings.audit_log_questions else None
    question_hash = (
        hashlib.sha256(question.encode("utf-8")).hexdigest() if question else None
    )
    await conn.execute(
        """
        INSERT INTO audit.events
            (actor, action, question, question_hash, document_ids, chunk_ids,
             conversation_id, model, meta)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
        """,
        actor,
        action,
        question_plain,
        question_hash,
        document_ids,
        chunk_ids,
        conversation_id,
        model,
        json.dumps(meta or {}),
    )
