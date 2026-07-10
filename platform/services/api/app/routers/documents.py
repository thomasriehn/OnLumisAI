"""Quellen-Viewer (Quick Win): liefert das Ursprungsdokument eines Zitats.

- ACL-geprüft: Nutzer ohne passende Gruppe erhalten 404 (Existenz wird nicht
  verraten).
- Dateisystem-Quellen werden gestreamt (Pfad-Traversal durch resolve()+
  Wurzel-Check ausgeschlossen); Remote-Quellen (Confluence/SharePoint/…)
  leiten auf die Original-Web-URL weiter.
"""

import json
import os
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

from .. import audit, db
from ..auth import User, get_current_user

router = APIRouter(prefix="/v1", tags=["documents"])

# Für die Inline-Anzeige im Browser lesbare Textformate
_INLINE_TEXT = {"text/markdown", "text/plain", None}


@router.get("/documents/{document_id}")
async def document_meta(
    document_id: UUID, user: User = Depends(get_current_user)
) -> dict:
    row = await _load_authorized(document_id, user)
    return {
        "id": str(row["id"]),
        "title": row["title"],
        "uri": row["uri"],
        "mime_type": row["mime_type"],
        "source": row["source_name"],
        "kind": row["kind"],
        "updated_at": row["updated_at"].isoformat(),
    }


@router.get("/documents/{document_id}/content")
async def document_content(
    document_id: UUID, user: User = Depends(get_current_user)
):
    row = await _load_authorized(document_id, user)
    async with db.pool().acquire() as conn:
        await audit.log_event(
            conn, user.username, "document_view",
            document_ids=[row["id"]],
        )

    if row["kind"] != "filesystem":
        return RedirectResponse(row["uri"], status_code=307)

    config = json.loads(row["config"])
    root = Path(config.get("root_path", "")).resolve()
    path = (root / row["external_id"]).resolve()
    if not root.is_dir() or not str(path).startswith(str(root) + os.sep) or not path.is_file():
        raise HTTPException(status_code=404, detail="Datei nicht verfügbar")

    media_type = row["mime_type"]
    if media_type in _INLINE_TEXT:
        media_type = "text/plain; charset=utf-8"  # MD/TXT im Browser anzeigen
    return FileResponse(
        path,
        media_type=media_type,
        filename=path.name,
        content_disposition_type="inline",
    )


async def _load_authorized(document_id: UUID, user: User):
    row = await db.pool().fetchrow(
        """
        SELECT d.id, d.external_id, d.uri, d.title, d.mime_type, d.acl_groups,
               d.updated_at, s.kind, s.config::text AS config, s.name AS source_name
        FROM knowledge.documents d
        JOIN knowledge.sources s ON s.id = d.source_id
        WHERE d.id = $1 AND d.deleted_at IS NULL
        """,
        document_id,
    )
    if row is None or not set(row["acl_groups"]) & set(user.groups):
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
    return row
