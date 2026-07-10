"""MCP-Server (AP 4.2, A4 „andere Tools"): stellt das Unternehmenswissen als
Model-Context-Protocol-Tools bereit – für interne Agenten, IDE-Assistenten
und Automatisierungen.

Transport: Streamable HTTP unter /mcp (stateless). Auth identisch zur REST-API
(API-Key, Dev-Header oder OIDC-Bearer) – die Header jedes MCP-Requests laufen
durch dieselbe get_current_user-Logik, ACLs greifen unverändert im Retrieval.
"""

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel

from . import audit, db, runtime
from .auth import User, ensure_scope, get_current_user
from .rag import build_messages, mark_used_citations
from .retrieval import retrieve

mcp = FastMCP(
    "onlumis",
    instructions=(
        "Zugriff auf das interne Unternehmenswissen von OnLumis. "
        "Antworten basieren ausschließlich auf freigegebenen Dokumenten "
        "und enthalten Quellenangaben."
    ),
    stateless_http=True,
)
# Unter /mcp gemountet (main.py) – interner Pfad daher "/".
mcp.settings.streamable_http_path = "/"


async def _current_user(ctx: Context) -> User:
    request = ctx.request_context.request
    if request is None:
        raise ValueError("Kein HTTP-Request-Kontext (Transport nicht unterstützt)")
    return await get_current_user(request)


@mcp.tool()
async def search_knowledge(query: str, top_k: int, ctx: Context) -> list[dict]:
    """Durchsucht das freigegebene Unternehmenswissen (Hybrid-Suche mit
    Berechtigungsprüfung) und liefert Fundstellen mit Quelle, Abschnitt und
    Textauszug. top_k: Anzahl der Treffer (1–20, üblich 8)."""
    user = await _current_user(ctx)
    ensure_scope(user, "search")
    top_k = max(1, min(int(top_k), 20))
    async with db.pool().acquire() as conn:
        chunks = await retrieve(runtime.gateway(), conn, query, user.groups, top_k=top_k)
        await audit.log_event(
            conn,
            user.username,
            "search",
            question=query,
            document_ids=list({c.document_id for c in chunks}),
            chunk_ids=[c.chunk_id for c in chunks],
            meta={"endpoint": "mcp"},
        )
    return [
        {
            "title": c.title,
            "uri": c.uri,
            "heading_path": c.heading_path,
            "page": c.page,
            "snippet": c.content[:400],
            "score": c.score,
        }
        for c in chunks
    ]


class McpAnswer(BaseModel):
    answer: str
    citations: list[dict]


@mcp.tool()
async def answer_with_sources(question: str, ctx: Context) -> McpAnswer:
    """Beantwortet eine Frage ausschließlich auf Basis des freigegebenen
    Unternehmenswissens. Liefert die Antwort und die zitierten Quellen;
    sagt offen, wenn die Wissensbasis keine Antwort hergibt."""
    user = await _current_user(ctx)
    ensure_scope(user, "chat")
    gateway = runtime.gateway()
    async with db.pool().acquire() as conn:
        chunks = await retrieve(gateway, conn, question, user.groups)
    messages, citations = build_messages(question, chunks)
    answer = await gateway.chat(messages)
    citations = mark_used_citations(answer, citations)
    async with db.pool().acquire() as conn:
        await audit.log_event(
            conn,
            user.username,
            "chat",
            question=question,
            document_ids=list({c.document_id for c in chunks}),
            chunk_ids=[c.chunk_id for c in chunks],
            meta={"endpoint": "mcp"},
        )
    return McpAnswer(answer=answer, citations=[c for c in citations if c["used"]])
