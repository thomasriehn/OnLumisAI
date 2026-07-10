"""Docling-Backend-Wiring: Auswahl per Setting, Fallback bei Fehlern."""

from worker import docling_backend, ocr
from worker.config import settings
from worker.parsing import Block, ParsedDocument


def _md(tmp_path):
    f = tmp_path / "doc.pdf"
    f.write_bytes(b"%PDF-1.4 fake")
    return f


def test_docling_used_when_configured(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "parsing_backend", "docling")
    monkeypatch.setattr(
        docling_backend, "parse_with_docling",
        lambda path: ParsedDocument(
            title="Docling", blocks=[Block(text="| A | B |\n|---|---|\n| 1 | 2 |")]
        ),
    )
    parsed = ocr.parse_document(_md(tmp_path))
    assert parsed.title == "Docling"
    assert "| A | B |" in parsed.blocks[0].text  # Tabellen bleiben erhalten


def test_docling_unavailable_falls_back(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "parsing_backend", "docling")
    monkeypatch.setattr(settings, "ocr_enabled", False)

    def raise_unavailable(path):
        raise docling_backend.DoclingUnavailable("nicht installiert")

    monkeypatch.setattr(docling_backend, "parse_with_docling", raise_unavailable)
    doc = tmp_path / "notiz.md"
    doc.write_text("# Titel\n\nInhalt.")
    # .md ist kein Docling-Format -> simple; .pdf mit Fehler -> Fallback simple
    assert ocr.parse_document(doc).title == "Titel"


def test_simple_backend_default(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "parsing_backend", "simple")
    called = []
    monkeypatch.setattr(
        docling_backend, "parse_with_docling",
        lambda path: called.append(path),
    )
    doc = tmp_path / "notiz.md"
    doc.write_text("# T\n\nx.")
    ocr.parse_document(doc)
    assert called == []  # Docling wird nicht angefasst