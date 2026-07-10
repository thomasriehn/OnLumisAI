from email.message import EmailMessage

from worker.connectors.imap import email_bytes_to_parsed


def _mail(subject: str, plain: str | None, html: str | None = None) -> bytes:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "support@firma.de"
    msg["To"] = "wissen@firma.de"
    msg["Date"] = "Fri, 10 Jul 2026 09:00:00 +0200"
    if plain is not None:
        msg.set_content(plain)
    if html is not None:
        if plain is not None:
            msg.add_alternative(html, subtype="html")
        else:
            msg.set_content(html, subtype="html")
    return bytes(msg)


def test_plain_text_mail():
    parsed, meta = email_bytes_to_parsed(
        _mail("Störung Presse P-300", "Ölstand war zu niedrig.\n\nHLP 46 nachgefüllt.")
    )
    assert parsed.title == "Störung Presse P-300"
    assert meta["from"] == "support@firma.de"
    texts = [b.text for b in parsed.blocks]
    assert any("Ölstand war zu niedrig." in t for t in texts)
    assert any("HLP 46 nachgefüllt." in t for t in texts)
    assert texts[0].startswith("Von: support@firma.de")


def test_prefers_plain_over_html():
    parsed, _ = email_bytes_to_parsed(
        _mail("Betreff", "Klartext-Inhalt.", "<p>HTML-Inhalt</p>")
    )
    assert any("Klartext-Inhalt." in b.text for b in parsed.blocks)


def test_html_only_mail():
    parsed, _ = email_bytes_to_parsed(
        _mail("HTML", None, "<h1>Anleitung</h1><p>Schritt eins.</p>")
    )
    assert any("Schritt eins." in b.text for b in parsed.blocks)
    assert any(b.heading_level == 1 for b in parsed.blocks)