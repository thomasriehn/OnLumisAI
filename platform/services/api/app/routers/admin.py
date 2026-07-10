"""Administration: Quellenverwaltung, Sync-Status, Basisstatistik (§6.1 Admin-Portal).

Alle Endpunkte erfordern die Gruppe aus ADMIN_GROUP (Default: onlumis-admin).
"""

import json
import re
import secrets
from pathlib import Path
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, UploadFile

from ..config import settings

from .. import audit, db
from ..auth import API_KEY_PREFIX, User, hash_api_key, require_admin
from ..schemas import (
    ApiKeyCreate,
    ApiKeyCreated,
    ApiKeyOut,
    SourceCreate,
    SourceOut,
    SourceUpdate,
    StatsOut,
)

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


def _api_key_out(row: asyncpg.Record) -> ApiKeyOut:
    return ApiKeyOut(
        id=row["id"],
        name=row["name"],
        key_prefix=row["key_prefix"],
        scopes=list(row["scopes"]),
        groups=list(row["groups"]),
        enabled=row["enabled"],
        created_by=row["created_by"],
        last_used_at=row["last_used_at"].isoformat() if row["last_used_at"] else None,
    )


@router.get("/api-keys", response_model=list[ApiKeyOut])
async def list_api_keys(user: User = Depends(require_admin)) -> list[ApiKeyOut]:
    rows = await db.pool().fetch("SELECT * FROM app.api_keys ORDER BY created_at")
    return [_api_key_out(r) for r in rows]


@router.post("/api-keys", response_model=ApiKeyCreated, status_code=201)
async def create_api_key(
    req: ApiKeyCreate, user: User = Depends(require_admin)
) -> ApiKeyCreated:
    key = API_KEY_PREFIX + secrets.token_urlsafe(32)
    async with db.pool().acquire() as conn:
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO app.api_keys (name, key_prefix, key_hash, scopes, groups, created_by)
                VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
                """,
                req.name,
                key[: len(API_KEY_PREFIX) + 6],
                hash_api_key(key),
                req.scopes,
                req.groups,
                user.username,
            )
        except asyncpg.UniqueViolationError as exc:
            raise HTTPException(status_code=409, detail="Key-Name bereits vergeben") from exc
        await audit.log_event(
            conn, user.username, "admin:apikey_created",
            meta={"name": req.name, "scopes": req.scopes, "groups": req.groups},
        )
    return ApiKeyCreated(**_api_key_out(row).model_dump(), key=key)


@router.patch("/api-keys/{key_id}", response_model=ApiKeyOut)
async def update_api_key(
    key_id: UUID, enabled: bool, user: User = Depends(require_admin)
) -> ApiKeyOut:
    async with db.pool().acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE app.api_keys SET enabled = $2 WHERE id = $1 RETURNING *",
            key_id,
            enabled,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="API-Key nicht gefunden")
        await audit.log_event(
            conn, user.username, "admin:apikey_updated",
            meta={"id": str(key_id), "enabled": enabled},
        )
    return _api_key_out(row)


@router.delete("/api-keys/{key_id}", status_code=204)
async def delete_api_key(key_id: UUID, user: User = Depends(require_admin)) -> None:
    async with db.pool().acquire() as conn:
        deleted = await conn.fetchval(
            "DELETE FROM app.api_keys WHERE id = $1 RETURNING id", key_id
        )
        if deleted is None:
            raise HTTPException(status_code=404, detail="API-Key nicht gefunden")
        await audit.log_event(
            conn, user.username, "admin:apikey_deleted", meta={"id": str(key_id)}
        )


_FILENAME_SAFE = re.compile(r"[^A-Za-z0-9äöüÄÖÜß._ -]+")


@router.post("/uploads", status_code=201)
async def upload_documents(
    files: list[UploadFile], user: User = Depends(require_admin)
) -> dict:
    """Upload-Portal (Quick Win): Dateien landen in der Quelle "uploads" und
    werden beim nächsten Sync-Lauf indexiert (Sichtbarkeit gemäß Quell-ACL,
    Default all-users – im Admin-Portal änderbar)."""
    uploads_dir = Path(settings.uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    async with db.pool().acquire() as conn:
        await conn.execute(
            """
            INSERT INTO knowledge.sources (kind, name, config, default_acl)
            VALUES ('filesystem', 'uploads', $1::jsonb, '{all-users}')
            ON CONFLICT (name) DO NOTHING
            """,
            json.dumps({"root_path": str(uploads_dir)}),
        )

    saved: list[str] = []
    for upload in files:
        name = _FILENAME_SAFE.sub("_", Path(upload.filename or "datei").name)
        target = uploads_dir / name
        counter = 1
        while target.exists():
            target = uploads_dir / f"{target.stem.rstrip('-0123456789') or 'datei'}-{counter}{target.suffix}"
            counter += 1
        target.write_bytes(await upload.read())
        saved.append(target.name)

    async with db.pool().acquire() as conn:
        await audit.log_event(
            conn, user.username, "admin:upload", meta={"files": saved}
        )
    return {
        "saved": saved,
        "hint": "Indexierung erfolgt mit dem nächsten Sync-Lauf der Quelle 'uploads'.",
    }


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
