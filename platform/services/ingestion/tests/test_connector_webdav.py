import httpx
import pytest

from worker.connectors.webdav import WebDavConnector


def _multistatus(entries: list[tuple[str, bool, str]]) -> str:
    parts = []
    for href, is_dir, etag in entries:
        rtype = "<d:collection/>" if is_dir else ""
        parts.append(f"""
        <d:response>
          <d:href>{href}</d:href>
          <d:propstat><d:prop>
            <d:resourcetype>{rtype}</d:resourcetype>
            <d:getetag>"{etag}"</d:getetag>
            <d:getlastmodified>Fri, 10 Jul 2026 09:00:00 GMT</d:getlastmodified>
          </d:prop></d:propstat>
        </d:response>""")
    return ('<?xml version="1.0"?><d:multistatus xmlns:d="DAV:">'
            + "".join(parts) + "</d:multistatus>")


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if request.method == "PROPFIND":
        assert request.headers["depth"] == "1"
        if path.rstrip("/").endswith("/webdav"):
            return httpx.Response(207, content=_multistatus([
                ("/webdav/", True, ""),
                ("/webdav/richtlinie.md", False, "e1"),
                ("/webdav/Unterordner", True, ""),
                ("/webdav/skript.exe", False, "e9"),
            ]))
        if path.endswith("/Unterordner"):
            return httpx.Response(207, content=_multistatus([
                ("/webdav/Unterordner/", True, ""),
                ("/webdav/Unterordner/anleitung.txt", False, "e2"),
            ]))
    if request.method == "GET" and path.endswith("richtlinie.md"):
        return httpx.Response(200, content=b"# Richtlinie\n\nInhalt aus dem DMS.")
    if request.method == "GET" and path.endswith("anleitung.txt"):
        return httpx.Response(200, content=b"Schritt 1: einschalten.")
    return httpx.Response(404)


@pytest.fixture()
def connector():
    return WebDavConnector(
        {"base_url": "https://dms.example.com/webdav",
         "username": "bot", "password": "pw"},
        http=httpx.AsyncClient(transport=httpx.MockTransport(_handler)),
    )


async def test_recursive_listing_filters_and_versions(connector):
    docs = [d async for d in connector.list_documents()]
    ids = sorted(d.external_id for d in docs)
    assert ids == ["Unterordner/anleitung.txt", "richtlinie.md"]  # .exe gefiltert
    assert {d.version for d in docs} == {"e1", "e2"}


async def test_fetch_parses_dms_content(connector):
    docs = {d.external_id: d async for d in connector.list_documents()}
    parsed = await connector.fetch(docs["richtlinie.md"])
    assert parsed.title == "Richtlinie"
    assert "Inhalt aus dem DMS" in " ".join(b.text for b in parsed.blocks)