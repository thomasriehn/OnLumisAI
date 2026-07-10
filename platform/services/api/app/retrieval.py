"""Hybrid-Retrieval: pgvector (HNSW) + Volltext (german) mit RRF-Fusion,
ACL-Filterung auf SQL-Ebene und optionalem Reranking (Architektur §6.4, §7.1).
"""

from dataclasses import dataclass
from uuid import UUID

import asyncpg

from .config import settings
from .llm import ModelGateway


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: UUID
    content: str
    heading_path: str | None
    page: int | None
    chunk_index: int
    title: str | None
    uri: str
    score: float


def to_pgvector(vec: list[float]) -> str:
    """Formatiert einen Vektor als pgvector-Literal ('[0.1,0.2,...]')."""
    return "[" + ",".join(f"{x:.7g}" for x in vec) + "]"


# $1 Query-Vektor (Literal), $2 Nutzergruppen, $3 Kandidaten je Verfahren,
# $4 Volltext-Query, $5 RRF-Konstante, $6 Ergebnis-Limit.
# ACL-Durchsetzung VOR dem Modell: nur Dokumente, deren acl_groups sich mit den
# Gruppen des Nutzers überschneiden (Prinzip 2 der Architektur).
HYBRID_SQL = """
WITH vec AS (
    SELECT c.id, row_number() OVER (ORDER BY c.embedding <=> $1::vector) AS rank
    FROM knowledge.chunks c
    JOIN knowledge.documents d ON d.id = c.document_id
    WHERE d.deleted_at IS NULL
      AND d.acl_groups && $2::text[]
    ORDER BY c.embedding <=> $1::vector
    LIMIT $3
),
fts AS (
    SELECT c.id, row_number() OVER (ORDER BY ts_rank_cd(c.tsv, q) DESC) AS rank
    FROM knowledge.chunks c
    JOIN knowledge.documents d ON d.id = c.document_id
    CROSS JOIN websearch_to_tsquery('german', $4) q
    WHERE d.deleted_at IS NULL
      AND d.acl_groups && $2::text[]
      AND c.tsv @@ q
    ORDER BY ts_rank_cd(c.tsv, q) DESC
    LIMIT $3
),
fused AS (
    SELECT COALESCE(v.id, f.id) AS id,
           COALESCE(1.0 / ($5 + v.rank), 0) + COALESCE(1.0 / ($5 + f.rank), 0) AS score
    FROM vec v
    FULL OUTER JOIN fts f ON v.id = f.id
)
SELECT fu.id AS chunk_id,
       fu.score::float8 AS score,
       c.content, c.heading_path, c.page, c.chunk_index,
       d.id AS document_id, d.title, d.uri
FROM fused fu
JOIN knowledge.chunks c ON c.id = fu.id
JOIN knowledge.documents d ON d.id = c.document_id
ORDER BY fu.score DESC, fu.id
LIMIT $6
"""


async def hybrid_search(
    conn: asyncpg.Connection,
    query_text: str,
    query_vec: list[float],
    user_groups: list[str],
    *,
    candidates: int | None = None,
    limit: int | None = None,
) -> list[RetrievedChunk]:
    rows = await conn.fetch(
        HYBRID_SQL,
        to_pgvector(query_vec),
        user_groups,
        candidates or settings.retrieval_candidates,
        query_text,
        settings.rrf_k,
        limit or settings.retrieval_candidates,
    )
    return [
        RetrievedChunk(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            content=r["content"],
            heading_path=r["heading_path"],
            page=r["page"],
            chunk_index=r["chunk_index"],
            title=r["title"],
            uri=r["uri"],
            score=r["score"],
        )
        for r in rows
    ]


async def retrieve(
    gateway: ModelGateway,
    conn: asyncpg.Connection,
    question: str,
    user_groups: list[str],
    *,
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """Kompletter Retrieval-Pfad: Embedding -> Hybrid-Suche -> Reranking -> Top-k."""
    top_k = top_k or settings.context_chunks
    query_vec = (await gateway.embed([question]))[0]
    candidates = await hybrid_search(conn, question, query_vec, user_groups)
    if not candidates:
        return []

    ranked = await gateway.rerank(question, [c.content for c in candidates], top_k)
    if ranked is None:  # kein Reranker konfiguriert -> RRF-Reihenfolge
        return candidates[:top_k]

    result = []
    for idx, score in ranked:
        chunk = candidates[idx]
        chunk.score = score
        result.append(chunk)
    return result
