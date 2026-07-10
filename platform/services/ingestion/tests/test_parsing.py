from worker.parsing import parse_html, parse_markdown, parse_text


def test_markdown_headings_and_title():
    doc = parse_markdown(
        "# Urlaubsrichtlinie\n\nIntro-Absatz.\n\n"
        "## Sonderurlaub\n\n- Hochzeit: 1 Tag\n- Umzug: 1 Tag\n\n"
        "```\ncode bleibt zusammen\n```\n"
    )
    assert doc.title == "Urlaubsrichtlinie"
    levels = [b.heading_level for b in doc.blocks if b.heading_level]
    assert levels == [1, 2]
    texts = " ".join(b.text for b in doc.blocks)
    assert "Hochzeit: 1 Tag" in texts
    assert "code bleibt zusammen" in texts


def test_markdown_no_heading():
    doc = parse_markdown("Nur ein Absatz ohne Überschrift.")
    assert doc.title is None
    assert len(doc.blocks) == 1


def test_text_paragraph_split():
    doc = parse_text("Absatz eins.\n\nAbsatz zwei.\n\n\nAbsatz drei.")
    assert [b.text for b in doc.blocks] == ["Absatz eins.", "Absatz zwei.", "Absatz drei."]


def test_html_structure_and_noise_removal():
    doc = parse_html(
        "<html><head><title>Wiki-Seite</title><style>p{}</style></head><body>"
        "<nav>Menü</nav><h1>Prozess</h1><p>Schritt eins.</p>"
        "<ul><li>Punkt A</li></ul><script>evil()</script></body></html>"
    )
    assert doc.title == "Wiki-Seite"
    texts = [b.text for b in doc.blocks]
    assert "Schritt eins." in texts
    assert "Punkt A" in texts
    assert all("Menü" not in t and "evil" not in t for t in texts)
