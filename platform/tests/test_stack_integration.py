"""Ende-zu-Ende-Integrationstest des RAG-Kerns (ohne LLM/GPU):

Ingestion-Pfad (Scan -> Parse -> Chunk -> Embed -> Upsert) über den echten
Worker-Code, danach Retrieval über den echten API-Code (Hybrid-SQL mit
RRF-Fusion) gegen pgvector – inklusive ACL-Negativtests (AP 2.3-Vorgriff)
und Tombstone-Verhalten (§7.2).
"""

import json
import shutil
from pathlib import Path

import asyncpg
import pytest

from app.retrieval import hybrid_search, retrieve
from tests.fake_models import FakeEmbedder, FakeGateway, fake_embedding
from worker.main import sync_filesystem_source

PLATFORM_ROOT = Path(__file__).resolve().parents[1]
SAMPLES = PLATFORM_ROOT / "data" / "sources" / "beispiel"


async def _add_source(pool: asyncpg.Pool, name: str, root: Path, acl: list[str]):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO knowledge.sources (kind, name, config, default_acl)
            VALUES ('filesystem', $1, $2::jsonb, $3)
            """,
            name,
            json.dumps({"root_path": str(root)}),
            acl,
        )
        return await conn.fetchrow(
            "SELECT id, name, kind, config::text AS config, default_acl "
            "FROM knowledge.sources WHERE name = $1",
            name,
        )


@pytest.fixture()
def corpus(tmp_path: Path) -> dict[str, Path]:
    """Zwei getrennte Quell-Verzeichnisse mit den Beispieldokumenten."""
    hr = tmp_path / "hr"
    produktion = tmp_path / "produktion"
    hr.mkdir()
    produktion.mkdir()
    shutil.copy(SAMPLES / "urlaubsrichtlinie.md", hr / "urlaubsrichtlinie.md")
    shutil.copy(SAMPLES / "wartung-presse-p300.md", produktion / "wartung-presse-p300.md")
    return {"hr": hr, "produktion": produktion}


async def _sync_all(pool, sources):
    embedder = FakeEmbedder()
    stats = {}
    for row in sources:
        stats[row["name"]] = await sync_filesystem_source(pool, embedder, row)
    return stats


async def test_ingest_retrieve_acl_and_tombstones(test_pool, corpus):
    hr_source = await _add_source(test_pool, "hr-docs", corpus["hr"], ["hr"])
    prod_source = await _add_source(
        test_pool, "produktions-docs", corpus["produktion"], ["produktion"]
    )

    # --- Ingestion: beide Quellen indexieren -------------------------------
    stats = await _sync_all(test_pool, [hr_source, prod_source])
    assert stats["hr-docs"].indexed == 1 and not stats["hr-docs"].errors
    assert stats["produktions-docs"].indexed == 1

    async with test_pool.acquire() as conn:
        chunk_count = await conn.fetchval("SELECT count(*) FROM knowledge.chunks")
        assert chunk_count >= 4  # beide Dokumente in mehrere Abschnitts-Chunks zerlegt
        sync_status = await conn.fetchval(
            "SELECT last_sync_status FROM knowledge.sources WHERE name = 'hr-docs'"
        )
        assert sync_status.startswith("ok")

    gateway = FakeGateway()

    # --- Semantik: Frage nach Sonderurlaub findet die Urlaubsrichtlinie ----
    async with test_pool.acquire() as conn:
        results = await retrieve(
            gateway, conn,
            "Wie viel Sonderurlaub gibt es bei einer Hochzeit?",
            ["hr", "produktion"],
        )
    assert results, "kein Treffer"
    assert "urlaubsrichtlinie" in results[0].uri
    assert "Hochzeit" in results[0].content
    assert results[0].heading_path and "Sonderurlaub" in results[0].heading_path

    # --- Volltext-Arm: exakter Fachbegriff (kein Embedding-Schlüsselwort) --
    async with test_pool.acquire() as conn:
        rows = await hybrid_search(
            conn, "Rückölfilter", fake_embedding("Rückölfilter"), ["produktion"]
        )
    assert rows and "Rückölfilter" in rows[0].content

    # --- ACL: HR sieht keine Produktionsdokumente (und umgekehrt) ----------
    async with test_pool.acquire() as conn:
        hr_view = await retrieve(
            gateway, conn, "Presse baut keinen Druck auf", ["hr"]
        )
        prod_view = await retrieve(
            gateway, conn, "Wie viel Sonderurlaub bei Hochzeit?", ["produktion"]
        )
    assert all("wartung" not in r.uri for r in hr_view)
    assert all("urlaubsrichtlinie" not in r.uri for r in prod_view)

    # Nutzer ohne passende Gruppe sieht überhaupt nichts
    async with test_pool.acquire() as conn:
        nothing = await retrieve(gateway, conn, "Urlaub", ["gast"])
    assert nothing == []

    # --- Idempotenz: zweiter Sync ohne Änderungen indexiert nichts neu ------
    stats2 = await _sync_all(test_pool, [hr_source, prod_source])
    assert stats2["hr-docs"].indexed == 0
    assert stats2["hr-docs"].unchanged == 1

    # --- Änderung: Datei anfassen -> genau ein Dokument neu indexiert -------
    doc = corpus["hr"] / "urlaubsrichtlinie.md"
    doc.write_text(doc.read_text() + "\n\n## Neu\n\nZusatzregel für Elternzeit.\n")
    stats3 = await _sync_all(test_pool, [hr_source, prod_source])
    assert stats3["hr-docs"].indexed == 1
    async with test_pool.acquire() as conn:
        results = await retrieve(gateway, conn, "Elternzeit Zusatzregel", ["hr"])
    assert results and "Elternzeit" in results[0].content

    # --- Tombstone: Datei löschen -> aus Suche verschwunden, Zeile bleibt ---
    doc.unlink()
    stats4 = await _sync_all(test_pool, [hr_source, prod_source])
    assert stats4["hr-docs"].removed == 1
    async with test_pool.acquire() as conn:
        gone = await retrieve(gateway, conn, "Sonderurlaub Hochzeit", ["hr"])
        tombstone = await conn.fetchrow(
            "SELECT deleted_at, (SELECT count(*) FROM knowledge.chunks c "
            " WHERE c.document_id = d.id) AS chunks "
            "FROM knowledge.documents d WHERE d.external_id = 'urlaubsrichtlinie.md'"
        )
    assert gone == []
    assert tombstone["deleted_at"] is not None
    assert tombstone["chunks"] == 0


async def test_audit_event_roundtrip(test_pool):
    """audit.log_event schreibt korrekt (Hash statt Klartext im Default)."""
    from app import audit
    from app.config import settings

    assert settings.audit_log_questions is False
    async with test_pool.acquire() as conn:
        await audit.log_event(
            conn, "alice", "chat", question="Geheime Frage?", model="chat"
        )
        row = await conn.fetchrow("SELECT * FROM audit.events")
    assert row["actor"] == "alice"
    assert row["question"] is None
    assert row["question_hash"] is not None and len(row["question_hash"]) == 64
