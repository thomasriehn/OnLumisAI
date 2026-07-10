"""Integrationstests gegen eine echte pgvector-Instanz.

Erwartet einen laufenden Container (siehe README bzw. CI):

    docker run -d --name onlumis-test-pg \
      -e POSTGRES_DB=onlumis -e POSTGRES_USER=onlumis -e POSTGRES_PASSWORD=test \
      -e KEYCLOAK_DB_PASSWORD=test -p 127.0.0.1:55432:5432 \
      pgvector/pgvector:pg17

Ist keine Instanz erreichbar, werden die Tests übersprungen.
Pro Test wird eine frische Datenbank mit dem echten Init-SQL angelegt.
"""

import os
import uuid
from pathlib import Path

import asyncpg
import pytest

PLATFORM_ROOT = Path(__file__).resolve().parents[1]
ADMIN_DSN = os.environ.get(
    "ONLUMIS_TEST_DSN", "postgresql://onlumis:test@127.0.0.1:55432/onlumis"
)


async def _admin_connect() -> asyncpg.Connection:
    return await asyncpg.connect(ADMIN_DSN)


@pytest.fixture()
async def test_dsn():
    try:
        admin = await _admin_connect()
    except OSError as exc:
        pytest.skip(f"Test-Postgres nicht erreichbar ({exc})")
        return

    dbname = f"onlumis_test_{uuid.uuid4().hex[:12]}"
    await admin.execute(f'CREATE DATABASE "{dbname}" OWNER onlumis')
    await admin.close()

    dsn = ADMIN_DSN.rsplit("/", 1)[0] + f"/{dbname}"
    conn = await asyncpg.connect(dsn)
    for sql_file in sorted((PLATFORM_ROOT / "db" / "init").glob("*.sql")):
        await conn.execute(sql_file.read_text())
    await conn.close()

    yield dsn

    admin = await _admin_connect()
    await admin.execute(f'DROP DATABASE "{dbname}" WITH (FORCE)')
    await admin.close()


@pytest.fixture()
async def test_pool(test_dsn):
    pool = await asyncpg.create_pool(test_dsn, min_size=1, max_size=4)
    yield pool
    await pool.close()


@pytest.fixture()
async def api_client(test_dsn, monkeypatch):
    """HTTP-Client gegen die echte FastAPI-App (ASGI) mit Test-DB + Fake-Modellen."""
    import httpx

    from app import db as api_db
    from app.config import settings as api_settings
    from app.main import app
    from tests.fake_models import FakeGateway

    monkeypatch.setattr(api_settings, "database_url", test_dsn)
    await api_db.init_pool()
    app.state.gateway = FakeGateway()
    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
            await seed_knowledge(api_db.pool())
            yield client
    finally:
        await api_db.close_pool()


async def seed_knowledge(pool) -> None:
    """Zwei Dokumente mit unterschiedlichen ACLs (hr / produktion)."""
    from worker.chunking import Chunk
    from worker.indexer import upsert_document

    from tests.fake_models import fake_embedding

    async with pool.acquire() as conn:
        source_id = await conn.fetchval(
            "INSERT INTO knowledge.sources (kind, name, config) "
            "VALUES ('filesystem', 'seed', '{}') RETURNING id"
        )
        docs = [
            ("hr/urlaub.md", ["hr"],
             "Sonderurlaub bei Hochzeit: 1 Tag. Urlaubsanspruch 30 Tage.",
             "Urlaubsrichtlinie › Sonderurlaub"),
            ("prod/presse.md", ["produktion"],
             "Presse Hydraulik: Wartung wöchentlich, Druck 190 bar.",
             "Wartung › Presse"),
        ]
        for external_id, acl, content, heading in docs:
            await upsert_document(
                conn,
                source_id=source_id,
                external_id=external_id,
                uri=f"file:///{external_id}",
                title=external_id,
                mime_type="text/markdown",
                content_hash=external_id,
                acl_groups=acl,
                meta={},
                chunks=[Chunk(index=0, content=content, heading_path=heading, page=None)],
                embeddings=[fake_embedding(content)],
            )
