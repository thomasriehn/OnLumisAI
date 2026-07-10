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
    for sql_file in ("001_extensions.sql", "002_schema.sql"):
        await conn.execute((PLATFORM_ROOT / "db" / "init" / sql_file).read_text())
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
