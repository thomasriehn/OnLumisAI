import httpx
import pytest

from worker.connectors.jira import JiraConnector

ISSUES = {
    "SUP-1": {"summary": "Presse ohne Druck", "updated": "2026-07-01T10:00:00.000+0200",
              "description": "Kunde meldet Druckabfall.\n\nDiagnose: Saugfilter.",
              "comments": [{"author": {"displayName": "Ines"}, "body": "Filter 88-1101 getauscht, gelöst."}]},
    "SUP-2": {"summary": "VPN-Zugang", "updated": "2026-07-02T09:00:00.000+0200",
              "description": None, "comments": []},
}


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path.endswith("/rest/api/2/search"):
        start = int(request.url.params.get("startAt", 0))
        keys = list(ISSUES) if start == 0 else []
        return httpx.Response(200, json={
            "total": len(ISSUES),
            "issues": [
                {"key": k, "fields": {"summary": ISSUES[k]["summary"],
                                      "updated": ISSUES[k]["updated"]}}
                for k in keys
            ],
        })
    for key, issue in ISSUES.items():
        if path.endswith(f"/rest/api/2/issue/{key}"):
            return httpx.Response(200, json={"fields": {
                "summary": issue["summary"],
                "description": issue["description"],
                "status": {"name": "Erledigt"},
                "comment": {"comments": issue["comments"]},
            }})
    return httpx.Response(404)


@pytest.fixture()
def connector():
    return JiraConnector(
        {"base_url": "https://firma.atlassian.net", "jql": "resolution = Done",
         "email": "bot@firma.de", "api_token": "t"},
        http=httpx.AsyncClient(transport=httpx.MockTransport(_handler)),
    )


async def test_list_issues(connector):
    docs = [d async for d in connector.list_documents()]
    assert [d.external_id for d in docs] == ["SUP-1", "SUP-2"]
    assert docs[0].uri.endswith("/browse/SUP-1")
    assert docs[0].version.startswith("2026-07-01")
    assert "Presse ohne Druck" in docs[0].title


async def test_fetch_includes_description_and_solution(connector):
    docs = [d async for d in connector.list_documents()]
    parsed = await connector.fetch(docs[0])
    text = " ".join(b.text for b in parsed.blocks)
    assert "Status: Erledigt" in text
    assert "Saugfilter" in text
    assert "Ines: Filter 88-1101 getauscht" in text
    headings = [b.text for b in parsed.blocks if b.heading_level]
    assert "Kommentare / Lösung" in headings