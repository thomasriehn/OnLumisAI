"""Audit-Einsicht und -Export (AP 2.4, A7) für DSB/IT-Sicherheit.

Zugriff: Rolle 'onlumis-auditor' oder 'onlumis-admin'. API-Keys nie.
"""

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from .. import db
from ..auth import User, require_auditor

router = APIRouter(prefix="/v1/audit", tags=["audit"])

_COLUMNS = [
    "id", "ts", "actor", "action", "question", "question_hash",
    "document_ids", "chunk_ids", "conversation_id", "model", "meta",
]


@router.get("/events")
async def list_events(
    user: User = Depends(require_auditor),
    since: datetime | None = None,
    until: datetime | None = None,
    actor: str | None = None,
    action: str | None = None,
    limit: int = Query(default=1000, ge=1, le=10000),
    format: str = Query(default="json", pattern="^(json|csv)$"),
):
    conditions, params = ["true"], []

    def add(condition: str, value) -> None:
        params.append(value)
        conditions.append(condition.format(n=len(params)))

    if since:
        add("ts >= ${n}", since)
    if until:
        add("ts <= ${n}", until)
    if actor:
        add("actor = ${n}", actor)
    if action:
        add("action = ${n}", action)
    params.append(limit)

    rows = await db.pool().fetch(
        f"""
        SELECT {", ".join(_COLUMNS)} FROM audit.events
        WHERE {" AND ".join(conditions)}
        ORDER BY ts DESC LIMIT ${len(params)}
        """,
        *params,
    )

    def serialize(row) -> dict:
        return {
            "id": row["id"],
            "ts": row["ts"].isoformat(),
            "actor": row["actor"],
            "action": row["action"],
            "question": row["question"],
            "question_hash": row["question_hash"],
            "document_ids": [str(d) for d in row["document_ids"] or []],
            "chunk_ids": list(row["chunk_ids"] or []),
            "conversation_id": str(row["conversation_id"]) if row["conversation_id"] else None,
            "model": row["model"],
            "meta": json.loads(row["meta"]) if isinstance(row["meta"], str) else row["meta"],
        }

    events = [serialize(r) for r in rows]

    if format == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=_COLUMNS)
        writer.writeheader()
        for event in events:
            writer.writerow(
                {
                    **event,
                    "document_ids": ";".join(event["document_ids"]),
                    "chunk_ids": ";".join(map(str, event["chunk_ids"])),
                    "meta": json.dumps(event["meta"], ensure_ascii=False),
                }
            )
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"content-disposition": "attachment; filename=audit-export.csv"},
        )
    return {"events": events, "count": len(events)}
