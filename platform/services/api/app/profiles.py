"""Abteilungs-Prompt-Profile (Antwortqualität): je Gruppe hinterlegte
Zusatzvorgaben für Stil/Format der Antworten. Mehrere Treffer werden
kombiniert; kein Treffer => None (Standard-Systemprompt)."""

import asyncpg


async def instructions_for(
    conn: asyncpg.Connection, groups: list[str]
) -> str | None:
    if not groups:
        return None
    rows = await conn.fetch(
        "SELECT instructions FROM app.prompt_profiles "
        "WHERE group_name = ANY($1::text[]) ORDER BY group_name",
        groups,
    )
    if not rows:
        return None
    return "\n".join(r["instructions"] for r in rows)
