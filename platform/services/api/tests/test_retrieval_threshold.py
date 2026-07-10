"""Konfidenz-Schwelle: schwache Reranker-Treffer werden verworfen."""

from uuid import uuid4

from app import retrieval
from app.config import settings
from app.retrieval import RetrievedChunk, retrieve


def _chunk(i: int) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=i, document_id=uuid4(), content=f"Inhalt {i}", heading_path=None,
        page=None, chunk_index=0, title=f"Doc {i}", uri=f"file:///d{i}", score=0.0,
    )


class RerankGateway:
    def __init__(self, ranked):
        self.ranked = ranked

    async def embed(self, texts):
        return [[0.0] * 4 for _ in texts]

    async def rerank(self, query, documents, top_n):
        return self.ranked


async def test_threshold_filters_weak_hits(monkeypatch):
    candidates = [_chunk(0), _chunk(1), _chunk(2)]

    async def fake_hybrid(conn, q, vec, groups, **kw):
        return candidates

    monkeypatch.setattr(retrieval, "hybrid_search", fake_hybrid)
    monkeypatch.setattr(settings, "min_rerank_score", 0.1)

    gateway = RerankGateway([(0, 0.92), (2, 0.31), (1, 0.04)])
    result = await retrieve(gateway, None, "Frage", ["hr"])
    assert [c.chunk_id for c in result] == [0, 2]  # 0.04 fällt raus
    assert result[0].score == 0.92


async def test_threshold_zero_keeps_all(monkeypatch):
    candidates = [_chunk(0), _chunk(1)]

    async def fake_hybrid(conn, q, vec, groups, **kw):
        return candidates

    monkeypatch.setattr(retrieval, "hybrid_search", fake_hybrid)
    monkeypatch.setattr(settings, "min_rerank_score", 0.0)
    gateway = RerankGateway([(1, 0.5), (0, 0.01)])
    result = await retrieve(gateway, None, "Frage", ["hr"])
    assert [c.chunk_id for c in result] == [1, 0]