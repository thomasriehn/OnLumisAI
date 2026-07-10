import httpx
import pytest

from worker.connectors.sharepoint import SharePointConnector

DELTA_PAGE_1 = {
    "value": [
        {"id": "A1", "name": "richtlinie.md", "eTag": "v1", "webUrl": "https://sp/x/richtlinie.md",
         "file": {"mimeType": "text/markdown"}, "parentReference": {"path": "/drive/root:/hr"}},
        {"id": "F1", "name": "Ordner", "folder": {}},                      # Ordner: überspringen
        {"id": "A2", "name": "tool.exe", "eTag": "v9", "file": {}},        # Format: überspringen
    ],
    "@odata.nextLink": "https://graph.microsoft.com/v1.0/drives/D/root/delta?page=2",
}
DELTA_PAGE_2 = {
    "value": [
        {"id": "A3", "name": "notiz.txt", "eTag": "v3", "webUrl": "https://sp/x/notiz.txt",
         "file": {"mimeType": "text/plain"}, "parentReference": {"path": "/drive/root:"}},
    ],
    "@odata.deltaLink": "https://graph.microsoft.com/v1.0/drives/D/root/delta?token=abc",
}

token_requests = []


def _handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if "login.microsoftonline.com" in url:
        token_requests.append(request)
        return httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
    assert request.headers.get("authorization") == "Bearer tok"
    if url.endswith("/root/delta"):
        return httpx.Response(200, json=DELTA_PAGE_1)
    if "delta?page=2" in url:
        return httpx.Response(200, json=DELTA_PAGE_2)
    if url.endswith("/items/A1/content"):
        return httpx.Response(200, content=b"# Richtlinie\n\nInhalt aus SharePoint.")
    return httpx.Response(404)


@pytest.fixture()
def connector():
    token_requests.clear()
    http = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
    return SharePointConnector(
        {"tenant_id": "t", "client_id": "c", "client_secret": "s", "drive_id": "D"},
        http=http,
    )


async def test_delta_paging_and_filtering(connector):
    docs = [d async for d in connector.list_documents()]
    assert [d.external_id for d in docs] == ["A1", "A3"]  # Ordner + .exe gefiltert
    assert docs[0].version == "v1"
    assert docs[0].meta["name"] == "richtlinie.md"


async def test_fetch_parses_content_and_caches_token(connector):
    docs = [d async for d in connector.list_documents()]
    parsed = await connector.fetch(docs[0])
    assert parsed.title == "Richtlinie"
    assert "Inhalt aus SharePoint" in " ".join(b.text for b in parsed.blocks)
    assert len(token_requests) == 1  # Token wird gecacht, nicht je Request geholt