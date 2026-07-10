"""Confluence-Konnektor (AP 3.3): Seiten ausgewählter Spaces über die REST-API.

Config (sources.config):
    {
      "base_url": "https://firma.atlassian.net/wiki",
      "space_keys": ["DOCS", "HR"],
      "email": "bot@firma.de",              # Cloud: Basic Auth mit API-Token
      "api_token": "..." | "api_token_env": "CONFLUENCE_TOKEN"
    }
Ohne "email" wird Bearer-Auth verwendet (Data Center / PAT).
Versionsstand: Confluence-Versionsnummer der Seite.
"""

from collections.abc import AsyncIterator

import httpx

from ..parsing import ParsedDocument, parse_html
from .base import RemoteConnector, RemoteDocument, secret_from_config

_PAGE_SIZE = 50


class ConfluenceConnector(RemoteConnector):
    kind = "confluence"

    def __init__(self, config: dict, http: httpx.AsyncClient | None = None) -> None:
        self.base_url = str(config["base_url"]).rstrip("/")
        self.space_keys: list[str] = list(config.get("space_keys", []))
        token = secret_from_config(config, "api_token")
        auth = httpx.BasicAuth(config["email"], token) if config.get("email") else None
        headers = {} if auth else {"Authorization": f"Bearer {token}"}
        self._http = http or httpx.AsyncClient(
            auth=auth, headers=headers, timeout=60, follow_redirects=True
        )
        self._owns_http = http is None

    async def list_documents(self) -> AsyncIterator[RemoteDocument]:
        for space in self.space_keys:
            start = 0
            while True:
                r = await self._http.get(
                    f"{self.base_url}/rest/api/content",
                    params={
                        "spaceKey": space,
                        "type": "page",
                        "status": "current",
                        "expand": "version",
                        "limit": _PAGE_SIZE,
                        "start": start,
                    },
                )
                r.raise_for_status()
                payload = r.json()
                for page in payload.get("results", []):
                    webui = page.get("_links", {}).get("webui", "")
                    yield RemoteDocument(
                        external_id=str(page["id"]),
                        uri=f"{self.base_url}{webui}" if webui else self.base_url,
                        version=str(page["version"]["number"]),
                        title=page.get("title"),
                        mime_type="text/html",
                        meta={"space": space},
                    )
                if len(payload.get("results", [])) < _PAGE_SIZE:
                    break
                start += _PAGE_SIZE

    async def fetch(self, doc: RemoteDocument) -> ParsedDocument:
        r = await self._http.get(
            f"{self.base_url}/rest/api/content/{doc.external_id}",
            params={"expand": "body.storage"},
        )
        r.raise_for_status()
        payload = r.json()
        parsed = parse_html(payload["body"]["storage"]["value"])
        return ParsedDocument(title=payload.get("title") or parsed.title, blocks=parsed.blocks)

    async def aclose(self) -> None:
        if self._owns_http:
            await self._http.aclose()
