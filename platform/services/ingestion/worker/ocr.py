"""OCR-Fallback für Bild-PDFs/Scans (AP 1.3-Ausbau, A2).

Aktiv, wenn ein PDF keinen extrahierbaren Text liefert und OCR_ENABLED gesetzt
ist. Benötigt die optionalen Abhängigkeiten (pip install .[ocr]) sowie die
Systempakete tesseract-ocr (+ Sprachpaket deu) und poppler-utils – im
Ingestion-Dockerfile über das Build-Arg WITH_OCR=1 aktivierbar.
"""

import logging
import re
from pathlib import Path

from .config import settings
from .parsing import Block, ParsedDocument, parse_file

logger = logging.getLogger("onlumis.ingestion")


class OcrUnavailable(RuntimeError):
    pass


def ocr_pdf_blocks(path: Path) -> list[Block]:
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError as exc:  # pragma: no cover - abhängig vom Deployment
        raise OcrUnavailable(
            "OCR-Abhängigkeiten fehlen (pip install .[ocr] + tesseract-ocr/poppler)"
        ) from exc

    blocks: list[Block] = []
    for page_no, image in enumerate(convert_from_path(str(path), dpi=200), start=1):
        text = pytesseract.image_to_string(image, lang=settings.ocr_languages)
        for para in re.split(r"\n\s*\n", text):
            if para.strip():
                blocks.append(Block(text=para.strip(), page=page_no))
    return blocks


def parse_with_ocr(path: Path) -> ParsedDocument:
    """parse_file mit OCR-Fallback für textlose PDFs (Scans)."""
    parsed = parse_file(path)
    if parsed.blocks or path.suffix.lower() != ".pdf" or not settings.ocr_enabled:
        return parsed
    try:
        blocks = ocr_pdf_blocks(path)
    except OcrUnavailable as exc:
        logger.warning("OCR nicht verfügbar für %s: %s", path.name, exc)
        return parsed
    logger.info("OCR angewendet: %s (%d Blöcke)", path.name, len(blocks))
    return ParsedDocument(title=parsed.title, blocks=blocks)
