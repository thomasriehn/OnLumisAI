"""Integrationstest der generischen Sync-Engine (AP 3.1) gegen pgvector."""

import json

from worker.connectors.base import RemoteConnector, RemoteDocument
from worker.engine import sync_remote_source
from worker.parsing import Block, ParsedDocument

from tests.fake_models import FakeEmbedder


class FakeRemoteConnector(RemoteConnector):
    kind = "confluence"  # beliebiger registrierter Typ

    def __init__(self, docs: dict[str, tuple[str, str]]):
        self.docs = docs  # external_id -> (version, text)
        self.fetch_calls: list[str] = []

    async def list_documents(self):
        for external_id, (version, _) in self.docs.items():
            yield RemoteDocument(
                external_id=external_id,
                uri=f"fake://{external_id}",
                version=version,
                title=external_id,
            )

    async def fetch(self, doc: RemoteDocument) -> ParsedDocument:
        self.fetch_calls.append(doc.external_id)
        _, text = self.docs[doc.external_id]
        if text == "RAISE":
            raise RuntimeError("kaputtes Dokument")
        return ParsedDocument(
            title=doc.title, blocks=[Block(text=text * 3)]  # über Mindestlänge
        )


async def _source(pool, name="wiki"):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO knowledge.sources (kind, name, config, default_acl) "
            "VALUES ('confluence', $1, $2::jsonb, $3)",
            name,
            json.dumps({}),
            ["all-users"],
        )
        return await conn.fetchrow(
            "SELECT id, name, kind, config::text AS config, default_acl "
            "FROM knowledge.sources WHERE name = $1",
            name,
        )


async def test_version_based_sync_and_tombstones(test_pool):
    source = await _source(test_pool)
    embedder = FakeEmbedder()
    connector = FakeRemoteConnector(
        {"p1": ("v1", "Reisekosten Pauschale 28 Euro. "),
         "p2": ("v1", "Onboarding erster Arbeitstag. ")}
    )

    stats = await sync_remote_source(test_pool, embedder, source, connector)
    assert (stats.indexed, stats.unchanged, stats.removed) == (2, 0, 0)

    # Unverändert: fetch wird nicht erneut aufgerufen (Versionsvergleich greift)
    connector.fetch_calls.clear()
    stats = await sync_remote_source(test_pool, embedder, source, connector)
    assert (stats.indexed, stats.unchanged) == (0, 2)
    assert connector.fetch_calls == []

    # Versionssprung: genau ein Dokument wird neu geholt
    connector.docs["p1"] = ("v2", "Reisekosten Pauschale 32 Euro ab 2027. ")
    stats = await sync_remote_source(test_pool, embedder, source, connector)
    assert (stats.indexed, stats.unchanged) == (1, 1)
    assert connector.fetch_calls == ["p1"]

    # Entfernt: Tombstone + Chunks weg
    del connector.docs["p2"]
    stats = await sync_remote_source(test_pool, embedder, source, connector)
    assert stats.removed == 1
    async with test_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT deleted_at, (SELECT count(*) FROM knowledge.chunks c "
            "WHERE c.document_id = d.id) AS chunks "
            "FROM knowledge.documents d WHERE external_id = 'p2'"
        )
    assert row["deleted_at"] is not None and row["chunks"] == 0


async def test_single_document_error_does_not_stop_sync(test_pool):
    source = await _source(test_pool, name="wiki2")
    connector = FakeRemoteConnector(
        {"ok": ("v1", "Gültiger Inhalt mit genug Länge. "), "bad": ("v1", "RAISE")}
    )
    stats = await sync_remote_source(test_pool, FakeEmbedder(), source, connector)
    assert stats.indexed == 1
    assert len(stats.errors) == 1 and "bad" in stats.errors[0]
    async with test_pool.acquire() as conn:
        status = await conn.fetchval(
            "SELECT last_sync_status FROM knowledge.sources WHERE name = 'wiki2'"
        )
    assert status.startswith("error:")