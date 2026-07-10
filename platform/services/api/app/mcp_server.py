"""MCP-Server (AP 4.2, A4 „andere Tools"): stellt das Unternehmenswissen als
Model-Context-Protocol-Tools bereit – für interne Agenten, IDE-Assistenten
und Automatisierungen.

Transport: Streamable HTTP unter /mcp (stateless). Auth identisch zur REST-API
(API-Key, Dev-Header oder OIDC-Bearer) – die Header jedes MCP-Requests laufen
durch dieselbe get_current_user-Logik, ACLs greifen unverändert im Retrieval.
"""

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel

from . import audit, db, gaps, profiles, runtime
from .auth import User, ensure_scope, get_current_user
from .rag import NO_CONTEXT_ANSWER, build_messages, mark_used_citations
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


# Sichere agentische Bausteine: reine Textentwürfe, keine Aktionen/Seiteneffekte.
DRAFT_STYLES: dict[str, str] = {
    "angebot": (
        "Formuliere einen Angebots-Textbaustein: professionell, konkret, mit "
        "Leistungsbeschreibung auf Basis des Kontexts. Keine Preise erfinden – "
        "fehlende Angaben als [PLATZHALTER] markieren."
    ),
    "email": (
        "Formuliere einen E-Mail-Entwurf (Anrede, klarer Kern, Grußformel), "
        "sachlich und knapp, fachliche Aussagen nur aus dem Kontext."
    ),
    "zusammenfassung": (
        "Erstelle eine strukturierte Zusammenfassung (Stichpunkte, dann "
        "3-Satz-Fazit) ausschließlich aus dem Kontext."
    ),
}


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
        extra = await profiles.instructions_for(conn, user.groups)
        if not chunks:
            await gaps.log_gap(conn, question, user)
    if not chunks:
        answer, citations = NO_CONTEXT_ANSWER, []
    else:
        messages, citations = build_messages(question, chunks, extra_instructions=extra)
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


@mcp.tool()
async def draft_text(kind: str, topic: str, ctx: Context) -> McpAnswer:
    """Erstellt einen Textbaustein-Entwurf aus dem Unternehmenswissen.
    kind: 'angebot' | 'email' | 'zusammenfassung'. Reiner Entwurf mit
    Quellen – es werden keine Aktionen ausgeführt oder Nachrichten versendet."""
    user = await _current_user(ctx)
    ensure_scope(user, "chat")
    style = DRAFT_STYLES.get(kind.lower().strip())
    if style is None:
        raise ValueError(f"Unbekannter Entwurfstyp: {kind} ({', '.join(DRAFT_STYLES)})")

    gateway = runtime.gateway()
    async with db.pool().acquire() as conn:
        chunks = await retrieve(gateway, conn, topic, user.groups)
        if not chunks:
            await gaps.log_gap(conn, topic, user)
    if not chunks:
        return McpAnswer(answer=NO_CONTEXT_ANSWER, citations=[])

    messages, citations = build_messages(
        f"Erstelle einen Entwurf zum Thema: {topic}", chunks, extra_instructions=style
    )
    answer = await gateway.chat(messages)
    citations = mark_used_citations(answer, citations)
    async with db.pool().acquire() as conn:
        await audit.log_event(
            conn, user.username, "draft",
            question=topic,
            document_ids=list({c.document_id for c in chunks}),
            meta={"endpoint": "mcp", "kind": kind},
        )
    return McpAnswer(answer=answer, citations=[c for c in citations if c["used"]])
