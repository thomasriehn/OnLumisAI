"""Administration: Quellenverwaltung, Sync-Status, Basisstatistik (§6.1 Admin-Portal).

Alle Endpunkte erfordern die Gruppe aus ADMIN_GROUP (Default: onlumis-admin).
"""

import json
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from .. import audit, db
from ..auth import User, require_admin
from ..schemas import SourceCreate, SourceOut, SourceUpdate, StatsOut

router = APIRouter(prefix="/v1/admin", tags=["admin"])


def _source_out(row: asyncpg.Record) -> SourceOut:
    return SourceOut(
        id=row["id"],
        name=row["name"],
        kind=row["kind"],
        config=json.loads(row["config"]),
        default_acl=list(row["default_acl"]),
        enabled=row["enabled"],
        last_sync_at=row["last_sync_at"].isoformat() if row["last_sync_at"] else None,
        last_sync_status=row["last_sync_status"],
        document_count=row["document_count"],
    )


_SOURCE_SELECT = """
SELECT s.id, s.name, s.kind, s.config::text AS config, s.default_acl, s.enabled,
       s.last_sync_at, s.last_sync_status,
       (SELECT count(*) FROM knowledge.documents d
         WHERE d.source_id = s.id AND d.deleted_at IS NULL)::int AS document_count
FROM knowledge.sources s
"""


@router.get("/sources", response_model=list[SourceOut])
async def list_sources(user: User = Depends(require_admin)) -> list[SourceOut]:
    async with db.pool().acquire() as conn:
        rows = await conn.fetch(_SOURCE_SELECT + " ORDER BY s.created_at")
    return [_source_out(r) for r in rows]


@router.post("/sources", response_model=SourceOut, status_code=201)
async def create_source(
    req: SourceCreate, user: User = Depends(require_admin)
) -> SourceOut:
    async with db.pool().acquire() as conn:
        try:
            source_id = await conn.fetchval(
                """
                INSERT INTO knowledge.sources (kind, name, config, default_acl, enabled)
                VALUES ($1, $2, $3::jsonb, $4, $5) RETURNING id
                """,
                req.kind,
                req.name,
                json.dumps(req.config),
                req.default_acl,
                req.enabled,
            )
        except asyncpg.UniqueViolationError as exc:
            raise HTTPException(status_code=409, detail="Quellenname bereits vergeben") from exc
        await audit.log_event(
            conn, user.username, "admin:source_created", meta={"source": req.name}
        )
        row = await conn.fetchrow(_SOURCE_SELECT + " WHERE s.id = $1", source_id)
    return _source_out(row)


@router.patch("/sources/{source_id}", response_model=SourceOut)
async def update_source(
    source_id: UUID, req: SourceUpdate, user: User = Depends(require_admin)
) -> SourceOut:
    async with db.pool().acquire() as conn:
        updated = await conn.fetchval(
            """
            UPDATE knowledge.sources SET
                config      = COALESCE($2::jsonb, config),
                default_acl = COALESCE($3, default_acl),
                enabled     = COALESCE($4, enabled)
            WHERE id = $1 RETURNING id
            """,
            source_id,
            json.dumps(req.config) if req.config is not None else None,
            req.default_acl,
            req.enabled,
        )
        if updated is None:
            raise HTTPException(status_code=404, detail="Quelle nicht gefunden")
        await audit.log_event(
            conn, user.username, "admin:source_updated", meta={"source_id": str(source_id)}
        )
        row = await conn.fetchrow(_SOURCE_SELECT + " WHERE s.id = $1", source_id)
    return _source_out(row)


@router.get("/stats", response_model=StatsOut)
async def stats(user: User = Depends(require_admin)) -> StatsOut:
    async with db.pool().acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
              (SELECT count(*) FROM knowledge.documents WHERE deleted_at IS NULL) AS documents,
              (SELECT count(*) FROM knowledge.chunks) AS chunks,
              (SELECT count(*) FROM app.conversations) AS conversations,
              (SELECT count(*) FROM app.feedback WHERE NOT reviewed) AS feedback_open
            """
        )
    return StatsOut(**dict(row))
