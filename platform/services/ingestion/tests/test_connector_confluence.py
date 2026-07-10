import httpx
import pytest

from worker.connectors.confluence import ConfluenceConnector

PAGES = {
    "1001": {"title": "Reisekostenrichtlinie", "version": 7,
             "body": "<h1>Reisekosten</h1><p>Pauschale 28 Euro pro Tag.</p>"},
    "1002": {"title": "Onboarding", "version": 2,
             "body": "<p>Erster Tag: IT-Ausstattung abholen.</p>"},
}


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path.endswith("/rest/api/content"):
        assert request.url.params["spaceKey"] == "DOCS"
        results = [
            {"id": pid, "title": p["title"], "version": {"number": p["version"]},
             "_links": {"webui": f"/spaces/DOCS/pages/{pid}"}}
            for pid, p in PAGES.items()
        ]
        return httpx.Response(200, json={"results": results})
    for pid, p in PAGES.items():
        if path.endswith(f"/rest/api/content/{pid}"):
            return httpx.Response(
                200,
                json={"title": p["title"], "body": {"storage": {"value": p["body"]}}},
            )
    return httpx.Response(404)


@pytest.fixture()
def connector():
    http = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
    return ConfluenceConnector(
        {"base_url": "https://wiki.example.com", "space_keys": ["DOCS"],
         "api_token": "t0ken"},
        http=http,
    )


async def test_list_documents(connector):
    docs = [d async for d in connector.list_documents()]
    assert len(docs) == 2
    first = docs[0]
    assert first.external_id == "1001"
    assert first.version == "7"
    assert first.uri == "https://wiki.example.com/spaces/DOCS/pages/1001"
    assert first.title == "Reisekostenrichtlinie"


async def test_fetch_parses_storage_html(connector):
    docs = [d async for d in connector.list_documents()]
    parsed = await connector.fetch(docs[0])
    assert parsed.title == "Reisekostenrichtlinie"
    texts = " ".join(b.text for b in parsed.blocks)
    assert "Pauschale 28 Euro" in texts
    assert any(b.heading_level == 1 for b in parsed.blocks)


async def test_secret_from_env(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_TOKEN", "aus-env")
    c = ConfluenceConnector(
        {"base_url": "https://w", "space_keys": [], "api_token_env": "CONFLUENCE_TOKEN"},
        http=httpx.AsyncClient(transport=httpx.MockTransport(_handler)),
    )
    assert c is not None  # Konstruktor wirft nicht -> Secret aufgelöst