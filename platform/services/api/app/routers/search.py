"""Intranet-Suche: Retrieval ohne Generierung (A4, Architektur §6.1)."""

from fastapi import APIRouter, Depends, Request

from .. import audit, db
from ..auth import User, ensure_scope
from ..config import settings
from ..rate import rate_limited_user
from ..retrieval import retrieve
from ..schemas import SearchRequest, SearchResponse, SearchResult

router = APIRouter(prefix="/v1", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(
    req: SearchRequest, request: Request, user: User = Depends(rate_limited_user)
) -> SearchResponse:
    ensure_scope(user, "search")
    gateway = request.app.state.gateway
    async with db.pool().acquire() as conn:
        chunks = await retrieve(gateway, conn, req.query, user.groups, top_k=req.top_k)
        await audit.log_event(
            conn,
            user.username,
            "search",
            question=req.query,
            document_ids=list({c.document_id for c in chunks}),
            chunk_ids=[c.chunk_id for c in chunks],
        )
    return SearchResponse(
        results=[
            SearchResult(
                title=c.title,
                uri=c.uri,
                page=c.page,
                heading_path=c.heading_path,
                snippet=c.content[: settings.max_snippet_chars],
                score=c.score,
                document_id=str(c.document_id),
                chunk_id=c.chunk_id,
            )
            for c in chunks
        ]
    )
