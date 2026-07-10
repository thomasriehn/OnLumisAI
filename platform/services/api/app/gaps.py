"""Wissenslücken-Erfassung (strategisch): Fragen ohne belastbare Quelle.

Die Frage ist das Arbeitsmaterial fürs Wissensmanagement und wird im Klartext
gespeichert; die Person wird pseudonymisiert (SHA-256). Auswertung über
GET /v1/admin/reports/knowledge-gaps.
"""

import hashlib

import asyncpg

from .auth import User


async def log_gap(conn: asyncpg.Connection, question: str, user: User) -> None:
    await conn.execute(
        "INSERT INTO app.knowledge_gaps (question, username_hash, groups) "
        "VALUES ($1, $2, $3)",
        question[:2000],
        hashlib.sha256(user.username.encode("utf-8")).hexdigest(),
        user.groups,
    )
