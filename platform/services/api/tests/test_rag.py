from uuid import uuid4

from app.rag import build_context, build_messages, mark_used_citations
from app.retrieval import RetrievedChunk


def _chunk(n: int, content: str, **kw) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=n,
        document_id=kw.get("document_id", uuid4()),
        content=content,
        heading_path=kw.get("heading_path"),
        page=kw.get("page"),
        chunk_index=0,
        title=kw.get("title", f"Doc {n}"),
        uri=kw.get("uri", f"file:///doc{n}.md"),
        score=1.0,
    )


def test_build_context_numbers_and_citations():
    chunks = [
        _chunk(1, "30 Urlaubstage pro Jahr.", heading_path="Urlaubsanspruch"),
        _chunk(2, "Sonderurlaub bei Hochzeit: 1 Tag.", page=3),
    ]
    context, citations = build_context(chunks)
    assert "[1] Doc 1 › Urlaubsanspruch" in context
    assert "[2] Doc 2 (Seite 3)" in context
    assert citations[0]["n"] == 1 and citations[1]["page"] == 3
    assert citations[1]["snippet"].startswith("Sonderurlaub")


def test_build_messages_with_history_and_empty_context():
    messages, citations = build_messages(
        "Wie viele Urlaubstage?", [], history=[{"role": "user", "content": "Hallo"}]
    )
    assert messages[0]["role"] == "system"
    assert messages[1] == {"role": "user", "content": "Hallo"}
    assert "keine passenden Dokumente" in messages[-1]["content"]
    assert citations == []


def test_context_prompt_marks_context_as_data():
    messages, _ = build_messages("Frage?", [_chunk(1, "Inhalt.")])
    system = messages[0]["content"]
    assert "Ignoriere" in system  # Guardrail gegen indirekte Prompt-Injection
    assert messages[-1]["content"].startswith("KONTEXT:")


def test_mark_used_citations():
    chunks = [_chunk(1, "A"), _chunk(2, "B"), _chunk(3, "C")]
    _, citations = build_context(chunks)
    answer = "Laut Richtlinie gilt X [1][3]. Weiteres ist nicht geregelt."
    marked = mark_used_citations(answer, citations)
    assert [c["used"] for c in marked] == [True, False, True]
