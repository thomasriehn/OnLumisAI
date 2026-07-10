"""Chat-Endpunkte: /v1/answers (RAG mit Quellen) und /v1/chat/completions
(OpenAI-kompatibel, optional gestreamt) sowie Konversations-Abruf.
"""

import json
from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from .. import audit, db
from ..auth import User, get_current_user
from ..config import settings
from ..llm import ModelGateway
from ..rag import build_messages, mark_used_citations
from ..retrieval import RetrievedChunk, retrieve
from ..schemas import AnswerRequest, AnswerResponse, ChatCompletionRequest, Citation

router = APIRouter(prefix="/v1", tags=["chat"])


def _gateway(request: Request) -> ModelGateway:
    return request.app.state.gateway


async def _load_owned_conversation(
    conn: asyncpg.Connection, conversation_id: UUID, user: User
) -> None:
    row = await conn.fetchrow(
        "SELECT username FROM app.conversations WHERE id = $1", conversation_id
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Konversation nicht gefunden")
    if row["username"] != user.username:
        raise HTTPException(status_code=403, detail="Fremde Konversation")


async def _history(conn: asyncpg.Connection, conversation_id: UUID) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT role, content FROM app.messages
        WHERE conversation_id = $1
        ORDER BY created_at DESC LIMIT $2
        """,
        conversation_id,
        settings.history_messages,
    )
    return [dict(r) for r in reversed(rows)]


async def _persist_exchange(
    conn: asyncpg.Connection,
    user: User,
    question: str,
    answer: str,
    citations: list[dict],
    chunks: list[RetrievedChunk],
    conversation_id: UUID | None,
) -> tuple[UUID, UUID]:
    async with conn.transaction():
        if conversation_id is None:
            conversation_id = await conn.fetchval(
                "INSERT INTO app.conversations (username, title) VALUES ($1, $2) RETURNING id",
                user.username,
                question[:80],
            )
        await conn.execute(
            "INSERT INTO app.messages (conversation_id, role, content) VALUES ($1, 'user', $2)",
            conversation_id,
            question,
        )
        message_id = await conn.fetchval(
            """
            INSERT INTO app.messages
                (conversation_id, role, content, citations, chunk_ids, model)
            VALUES ($1, 'assistant', $2, $3::jsonb, $4, $5)
            RETURNING id
            """,
            conversation_id,
            answer,
            json.dumps(citations, ensure_ascii=False),
            [c.chunk_id for c in chunks],
            settings.chat_model,
        )
    return conversation_id, message_id


@router.post("/answers", response_model=AnswerResponse)
async def answers(
    req: AnswerRequest, request: Request, user: User = Depends(get_current_user)
) -> AnswerResponse:
    gateway = _gateway(request)

    async with db.pool().acquire() as conn:
        history: list[dict] = []
        if req.conversation_id is not None:
            await _load_owned_conversation(conn, req.conversation_id, user)
            history = await _history(conn, req.conversation_id)
        chunks = await retrieve(gateway, conn, req.question, user.groups, top_k=req.top_k)

    messages, citations = build_messages(req.question, chunks, history)
    answer = await gateway.chat(messages)
    citations = mark_used_citations(answer, citations)

    async with db.pool().acquire() as conn:
        conversation_id, message_id = await _persist_exchange(
            conn, user, req.question, answer, citations, chunks, req.conversation_id
        )
        await audit.log_event(
            conn,
            user.username,
            "chat",
            question=req.question,
            document_ids=list({c.document_id for c in chunks}),
            chunk_ids=[c.chunk_id for c in chunks],
            conversation_id=conversation_id,
            model=settings.chat_model,
        )

    return AnswerResponse(
        answer=answer,
        citations=[Citation(**c) for c in citations],
        conversation_id=conversation_id,
        message_id=message_id,
        model=settings.chat_model,
    )


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


@router.post("/chat/completions")
async def chat_completions(
    req: ChatCompletionRequest, request: Request, user: User = Depends(get_current_user)
):
    """OpenAI-kompatibel; RAG ist standardmäßig aktiv (metadata: {"rag": false}
    deaktiviert es). Zitate kommen als zusätzliches SSE-Event
    {"object": "onlumis.citations"} vor [DONE] bzw. als Feld "onlumis" in der
    Non-Streaming-Antwort. Mit metadata {"persist": true} wird der Austausch
    als Konversation gespeichert (liefert conversation_id/message_id für
    Feedback); metadata.conversation_id setzt eine bestehende fort.
    """
    gateway = _gateway(request)
    meta = req.metadata or {}
    rag_enabled = bool(meta.get("rag", True))
    persist = bool(meta.get("persist", False))

    conversation_id: UUID | None = None
    if meta.get("conversation_id"):
        try:
            conversation_id = UUID(str(meta["conversation_id"]))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="conversation_id ungültig") from exc

    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if last_user is None:
        raise HTTPException(status_code=400, detail="Mindestens eine user-Message nötig")

    if persist and conversation_id is not None:
        async with db.pool().acquire() as conn:
            await _load_owned_conversation(conn, conversation_id, user)

    chunks: list[RetrievedChunk] = []
    citations: list[dict] = []
    if rag_enabled:
        async with db.pool().acquire() as conn:
            chunks = await retrieve(gateway, conn, last_user.content, user.groups)
        history = [
            m.model_dump() for m in req.messages[:-1] if m.role in ("user", "assistant")
        ]
        messages, citations = build_messages(last_user.content, chunks, history)
    else:
        messages = [m.model_dump() for m in req.messages]

    overrides = {"temperature": req.temperature, "max_tokens": req.max_tokens}
    completion_id = f"chatcmpl-{uuid4().hex}"

    async def _audit(question: str, answer: str, cid: UUID | None) -> None:
        async with db.pool().acquire() as conn:
            await audit.log_event(
                conn,
                user.username,
                "chat",
                question=question,
                document_ids=list({c.document_id for c in chunks}),
                chunk_ids=[c.chunk_id for c in chunks],
                conversation_id=cid,
                model=settings.chat_model,
                meta={"endpoint": "chat/completions", "rag": rag_enabled},
            )

    async def _maybe_persist(answer: str, marked: list[dict]) -> dict:
        """Persistiert bei metadata.persist und liefert die IDs für das Event."""
        if not persist:
            return {}
        async with db.pool().acquire() as conn:
            cid, mid = await _persist_exchange(
                conn, user, last_user.content, answer, marked, chunks, conversation_id
            )
        return {"conversation_id": str(cid), "message_id": str(mid)}

    if not req.stream:
        answer = await gateway.chat(messages, **overrides)
        citations = mark_used_citations(answer, citations)
        ids = await _maybe_persist(answer, citations)
        await _audit(
            last_user.content, answer,
            UUID(ids["conversation_id"]) if ids else conversation_id,
        )
        return {
            "id": completion_id,
            "object": "chat.completion",
            "model": settings.chat_model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": answer},
                    "finish_reason": "stop",
                }
            ],
            "onlumis": {"citations": citations, **ids},
        }

    async def stream() -> AsyncIterator[str]:
        def chunk_payload(delta: dict, finish: str | None = None) -> dict:
            return {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "model": settings.chat_model,
                "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
            }

        yield _sse(chunk_payload({"role": "assistant"}))
        collected: list[str] = []
        async for delta in gateway.chat_stream(messages, **overrides):
            collected.append(delta)
            yield _sse(chunk_payload({"content": delta}))
        yield _sse(chunk_payload({}, finish="stop"))

        answer = "".join(collected)
        marked = mark_used_citations(answer, citations)
        ids = await _maybe_persist(answer, marked)
        yield _sse({"object": "onlumis.citations", "citations": marked, **ids})
        yield "data: [DONE]\n\n"
        await _audit(
            last_user.content, answer,
            UUID(ids["conversation_id"]) if ids else conversation_id,
        )

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.get("/conversations")
async def list_conversations(user: User = Depends(get_current_user)) -> list[dict]:
    async with db.pool().acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, title, created_at FROM app.conversations
            WHERE username = $1 ORDER BY created_at DESC LIMIT 50
            """,
            user.username,
        )
    return [
        {"id": str(r["id"]), "title": r["title"], "created_at": r["created_at"].isoformat()}
        for r in rows
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: UUID, user: User = Depends(get_current_user)
) -> dict:
    async with db.pool().acquire() as conn:
        await _load_owned_conversation(conn, conversation_id, user)
        rows = await conn.fetch(
            """
            SELECT id, role, content, citations, created_at FROM app.messages
            WHERE conversation_id = $1 ORDER BY created_at
            """,
            conversation_id,
        )
    return {
        "id": str(conversation_id),
        "messages": [
            {
                "id": str(r["id"]),
                "role": r["role"],
                "content": r["content"],
                "citations": json.loads(r["citations"]) if r["citations"] else [],
                "created_at": r["created_at"].isoformat(),
            }
            for r in rows
        ],
    }
