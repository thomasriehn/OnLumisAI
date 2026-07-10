from pypdf import PdfWriter

from worker import ocr
from worker.parsing import Block


def _blank_pdf(path):
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)  # Seite ohne Textebene (wie ein Scan)
    with path.open("wb") as fh:
        writer.write(fh)


def test_ocr_fallback_for_scanned_pdf(tmp_path, monkeypatch):
    pdf = tmp_path / "scan.pdf"
    _blank_pdf(pdf)

    monkeypatch.setattr(
        ocr, "ocr_pdf_blocks",
        lambda path: [Block(text="Erkannter Scan-Inhalt: Wartungsplan.", page=1)],
    )
    parsed = ocr.parse_with_ocr(pdf)
    assert parsed.blocks[0].text.startswith("Erkannter Scan-Inhalt")
    assert parsed.blocks[0].page == 1


def test_no_ocr_when_disabled(tmp_path, monkeypatch):
    from worker.config import settings

    pdf = tmp_path / "scan.pdf"
    _blank_pdf(pdf)
    monkeypatch.setattr(settings, "ocr_enabled", False)
    monkeypatch.setattr(
        ocr, "ocr_pdf_blocks", lambda path: (_ for _ in ()).throw(AssertionError)
    )
    assert ocr.parse_with_ocr(pdf).blocks == []


def test_ocr_unavailable_degrades_gracefully(tmp_path, monkeypatch):
    pdf = tmp_path / "scan.pdf"
    _blank_pdf(pdf)

    def _raise(path):
        raise ocr.OcrUnavailable("keine Abhängigkeiten")

    monkeypatch.setattr(ocr, "ocr_pdf_blocks", _raise)
    assert ocr.parse_with_ocr(pdf).blocks == []  # kein Crash, Dokument bleibt leer


def test_text_pdf_skips_ocr(tmp_path, monkeypatch):
    # Markdown-Datei: parse_with_ocr delegiert nur an parse_file
    doc = tmp_path / "notiz.md"
    doc.write_text("# Titel\n\nInhalt der Notiz.")
    monkeypatch.setattr(
        ocr, "ocr_pdf_blocks", lambda path: (_ for _ in ()).throw(AssertionError)
    )
    parsed = ocr.parse_with_ocr(doc)
    assert parsed.title == "Titel"