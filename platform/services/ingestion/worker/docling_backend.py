"""Docling-Parsing-Backend (ADR-6, Antwortqualität): Layout-/Tabellen-
erkennung für PDF/DOCX & Co. Optional (pip install .[docling]) und über
PARSING_BACKEND=docling aktivierbar; bei Fehlern fällt die Pipeline auf das
einfache Backend zurück – kein Dokument bleibt deswegen unindexiert.
"""

from pathlib import Path

from .parsing import ParsedDocument, parse_markdown


class DoclingUnavailable(RuntimeError):
    pass


_converter = None


def parse_with_docling(path: Path) -> ParsedDocument:
    global _converter
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:  # pragma: no cover - abhängig vom Deployment
        raise DoclingUnavailable(
            "Docling nicht installiert (pip install .[docling])"
        ) from exc

    if _converter is None:
        _converter = DocumentConverter()
    result = _converter.convert(str(path))
    # Markdown-Export erhält Überschriften-Struktur und Tabellen (als
    # Markdown-Tabellen) -> unser strukturbewusstes Chunking greift direkt.
    markdown = result.document.export_to_markdown()
    parsed = parse_markdown(markdown)
    return ParsedDocument(title=parsed.title or path.stem, blocks=parsed.blocks)
