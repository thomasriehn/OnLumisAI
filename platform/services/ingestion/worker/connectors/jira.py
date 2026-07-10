"""Jira-Konnektor (Ticketsysteme): Issues inkl. Kommentare als Wissensquelle.

Config (sources.config):
    {
      "base_url": "https://firma.atlassian.net",
      "jql": "project = SUP AND resolution = Done",   # Freigabe-Filter!
      "email": "bot@firma.de",                         # Cloud: Basic + API-Token
      "api_token": "..." | "api_token_env": "JIRA_TOKEN"
    }
Ohne "email" wird Bearer-Auth verwendet (Data Center PAT).
Versionsstand: updated-Zeitstempel des Issues.
"""

from collections.abc import AsyncIterator

import httpx

from ..parsing import Block, ParsedDocument
from .base import RemoteConnector, RemoteDocument, secret_from_config

_PAGE_SIZE = 50


class JiraConnector(RemoteConnector):
    kind = "jira"

    def __init__(self, config: dict, http: httpx.AsyncClient | None = None) -> None:
        self.base_url = str(config["base_url"]).rstrip("/")
        self.jql = str(config.get("jql", "resolution = Done"))
        token = secret_from_config(config, "api_token")
        auth = httpx.BasicAuth(config["email"], token) if config.get("email") else None
        headers = {} if auth else {"Authorization": f"Bearer {token}"}
        self._http = http or httpx.AsyncClient(auth=auth, headers=headers, timeout=60)
        self._owns_http = http is None

    async def list_documents(self) -> AsyncIterator[RemoteDocument]:
        start = 0
        while True:
            r = await self._http.get(
                f"{self.base_url}/rest/api/2/search",
                params={
                    "jql": self.jql,
                    "fields": "summary,updated",
                    "startAt": start,
                    "maxResults": _PAGE_SIZE,
                },
            )
            r.raise_for_status()
            payload = r.json()
            for issue in payload.get("issues", []):
                yield RemoteDocument(
                    external_id=issue["key"],
                    uri=f"{self.base_url}/browse/{issue['key']}",
                    version=str(issue["fields"]["updated"]),
                    title=f"{issue['key']}: {issue['fields'].get('summary', '')}",
                    mime_type="text/plain",
                )
            start += _PAGE_SIZE
            if start >= int(payload.get("total", 0)):
                break

    async def fetch(self, doc: RemoteDocument) -> ParsedDocument:
        r = await self._http.get(
            f"{self.base_url}/rest/api/2/issue/{doc.external_id}",
            params={"fields": "summary,description,comment,status,resolution"},
        )
        r.raise_for_status()
        fields = r.json()["fields"]
        blocks: list[Block] = []
        status = (fields.get("status") or {}).get("name", "")
        blocks.append(Block(text=f"Ticket {doc.external_id} · Status: {status}"))
        if fields.get("description"):
            blocks.append(Block(text="Beschreibung", heading_level=2))
            blocks.extend(
                Block(text=p.strip())
                for p in str(fields["description"]).split("\n\n")
                if p.strip()
            )
        comments = (fields.get("comment") or {}).get("comments", [])
        if comments:
            blocks.append(Block(text="Kommentare / Lösung", heading_level=2))
            for comment in comments:
                author = (comment.get("author") or {}).get("displayName", "")
                blocks.append(Block(text=f"{author}: {comment.get('body', '')}"))
        return ParsedDocument(title=doc.title, blocks=blocks)

    async def aclose(self) -> None:
        if self._owns_http:
            await self._http.aclose()
