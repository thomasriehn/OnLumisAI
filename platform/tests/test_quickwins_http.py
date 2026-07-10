"""HTTP-Tests: Quellen-Viewer, Konversations-Löschung, Upload-Portal, Retention."""

import json

from tests.fake_models import fake_embedding
from worker.chunking import Chunk
from worker.indexer import upsert_document

HR = {"X-Dev-User": "hanna", "X-Dev-Groups": "hr"}
PROD = {"X-Dev-User": "paul", "X-Dev-Groups": "produktion"}
ADMIN = {"X-Dev-User": "root", "X-Dev-Groups": "all-users,onlumis-admin"}


async def _seed_file_doc(pool, tmp_path, *, acl=("hr",)):
    root = tmp_path / "quelle"
    root.mkdir(exist_ok=True)
    f = root / "richtlinie.md"
    f.write_text("# Richtlinie\n\nSonderurlaub bei Hochzeit: 1 Tag.")
    async with pool.acquire() as conn:
        source_id = await conn.fetchval(
            "INSERT INTO knowledge.sources (kind, name, config) "
            "VALUES ('filesystem', 'datei-quelle', $1::jsonb) RETURNING id",
            json.dumps({"root_path": str(root)}),
        )
        doc_id = await upsert_document(
            conn,
            source_id=source_id,
            external_id="richtlinie.md",
            uri=f.as_uri(),
            title="Richtlinie",
            mime_type="text/markdown",
            content_hash="h1",
            acl_groups=list(acl),
            meta={},
            chunks=[Chunk(index=0, content="Sonderurlaub bei Hochzeit: 1 Tag.",
                          heading_path="Richtlinie", page=None)],
            embeddings=[fake_embedding("sonderurlaub hochzeit")],
        )
    return doc_id


async def test_document_viewer_acl_and_content(api_client, tmp_path):
    from app import db as api_db

    doc_id = await _seed_file_doc(api_db.pool(), tmp_path)

    # Berechtigte Nutzerin: Metadaten + Inhalt inline
    r = await api_client.get(f"/v1/documents/{doc_id}", headers=HR)
    assert r.status_code == 200 and r.json()["title"] == "Richtlinie"
    r = await api_client.get(f"/v1/documents/{doc_id}/content", headers=HR)
    assert r.status_code == 200
    assert "Sonderurlaub bei Hochzeit" in r.text
    assert r.headers["content-type"].startswith("text/plain")
    assert "inline" in r.headers.get("content-disposition", "")

    # Fremde Gruppe: 404 (Existenz wird nicht verraten)
    r = await api_client.get(f"/v1/documents/{doc_id}/content", headers=PROD)
    assert r.status_code == 404


async def test_document_viewer_blocks_traversal(api_client, tmp_path):
    from app import db as api_db

    pool = api_db.pool()
    (tmp_path / "geheim.txt").write_text("ausserhalb der Quelle")
    root = tmp_path / "quelle"
    async with pool.acquire() as conn:
        source_id = await conn.fetchval(
            "SELECT id FROM knowledge.sources WHERE name = 'datei-quelle'"
        ) or await conn.fetchval(
            "INSERT INTO knowledge.sources (kind, name, config) "
            "VALUES ('filesystem', 'datei-quelle', $1::jsonb) RETURNING id",
            json.dumps({"root_path": str(root)}),
        )
        doc_id = await upsert_document(
            conn,
            source_id=source_id,
            external_id="../geheim.txt",  # Traversal-Versuch
            uri="file:///x",
            title="x",
            mime_type="text/plain",
            content_hash="h2",
            acl_groups=["hr"],
            meta={},
            chunks=[Chunk(index=0, content="x" * 30, heading_path=None, page=None)],
            embeddings=[fake_embedding("x")],
        )
    r = await api_client.get(f"/v1/documents/{doc_id}/content", headers=HR)
    assert r.status_code == 404  # resolve()-Check verhindert Ausbruch


async def test_conversation_delete(api_client):
    r = await api_client.post("/v1/answers", headers=HR, json={"question": "Urlaub?"})
    cid = r.json()["conversation_id"]

    # Fremder Nutzer darf nicht löschen
    r = await api_client.delete(f"/v1/conversations/{cid}", headers=PROD)
    assert r.status_code == 403
    # Eigentümerin löscht; danach 404
    r = await api_client.delete(f"/v1/conversations/{cid}", headers=HR)
    assert r.status_code == 204
    r = await api_client.get(f"/v1/conversations/{cid}", headers=HR)
    assert r.status_code == 404


async def test_upload_portal(api_client, tmp_path, monkeypatch):
    from app import db as api_db
    from app.config import settings as api_settings

    monkeypatch.setattr(api_settings, "uploads_dir", str(tmp_path / "uploads"))

    files = [
        ("files", ("notiz.md", b"# Notiz\n\nInhalt.", "text/markdown")),
        ("files", ("böse/../pfad.md", b"x", "text/markdown")),
    ]
    r = await api_client.post("/v1/admin/uploads", headers=ADMIN, files=files)
    assert r.status_code == 201
    saved = r.json()["saved"]
    assert "notiz.md" in saved
    assert all("/" not in name and ".." not in name for name in saved)
    assert (tmp_path / "uploads" / "notiz.md").read_bytes().startswith(b"# Notiz")

    # Quelle "uploads" wurde automatisch registriert
    row = await api_db.pool().fetchrow(
        "SELECT kind, config::text AS config FROM knowledge.sources WHERE name='uploads'"
    )
    assert row["kind"] == "filesystem"
    assert str(tmp_path / "uploads") in row["config"]

    # Namenskollision bekommt Suffix
    r = await api_client.post(
        "/v1/admin/uploads", headers=ADMIN,
        files=[("files", ("notiz.md", b"neu", "text/markdown"))],
    )
    assert r.json()["saved"] != ["notiz.md"]

    # Kein Admin -> 403
    r = await api_client.post(
        "/v1/admin/uploads", headers=HR,
        files=[("files", ("x.md", b"x", "text/markdown"))],
    )
    assert r.status_code == 403


async def test_retention_purges_old_data(api_client, monkeypatch):
    from app import db as api_db
    from app.config import settings as api_settings
    from app.retention import purge_once

    pool = api_db.pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO app.conversations (username, title, created_at) "
            "VALUES ('alt', 'alt', now() - interval '40 days')"
        )
        await conn.execute(
            "INSERT INTO app.conversations (username, title) VALUES ('neu', 'neu')"
        )
        await conn.execute(
            "INSERT INTO audit.events (actor, action, ts) "
            "VALUES ('alt', 'chat', now() - interval '400 days')"
        )

    # Deaktiviert (0): nichts passiert
    removed = await purge_once(pool)
    assert removed == {"conversations": 0, "audit_events": 0}

    monkeypatch.setattr(api_settings, "retention_days_conversations", 30)
    monkeypatch.setattr(api_settings, "retention_days_audit", 365)
    removed = await purge_once(pool)
    assert removed["conversations"] == 1
    assert removed["audit_events"] == 1
    async with pool.acquire() as conn:
        remaining = await conn.fetchval("SELECT count(*) FROM app.conversations")
    assert remaining == 1  # die neue bleibt