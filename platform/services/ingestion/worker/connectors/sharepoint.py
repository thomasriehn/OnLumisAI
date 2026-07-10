"""SharePoint/OneDrive-Konnektor (AP 3.2) über die Microsoft-Graph-API.

Config (sources.config):
    {
      "tenant_id": "...",
      "client_id": "...",
      "client_secret": "..." | "client_secret_env": "GRAPH_CLIENT_SECRET",
      "drive_id": "b!..."          # Dokumentbibliothek (Graph-Drive-ID)
    }
App-Registrierung benötigt die Application-Permission Files.Read.All (bzw.
Sites.Read.All). Versionsstand: Graph-eTag des Drive-Items. Jeder Sync
enumeriert den Drive vollständig über /root/delta ohne gespeicherten
Delta-Token (persistierte Delta-Tokens: Ausbaustufe).
"""

import time
from collections.abc import AsyncIterator
from pathlib import PurePosixPath

import httpx

from ..parsing import SUPPORTED_EXTENSIONS, ParsedDocument, parse_bytes
from .base import RemoteConnector, RemoteDocument, secret_from_config

GRAPH = "https://graph.microsoft.com/v1.0"


class SharePointConnector(RemoteConnector):
    kind = "sharepoint"

    def __init__(self, config: dict, http: httpx.AsyncClient | None = None) -> None:
        self.tenant_id = str(config["tenant_id"])
        self.client_id = str(config["client_id"])
        self.client_secret = secret_from_config(config, "client_secret")
        self.drive_id = str(config["drive_id"])
        self._http = http or httpx.AsyncClient(timeout=120, follow_redirects=True)
        self._owns_http = http is None
        self._token: str | None = None
        self._token_expires_at = 0.0

    async def _access_token(self) -> str:
        if self._token and time.monotonic() < self._token_expires_at - 60:
            return self._token
        r = await self._http.post(
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "https://graph.microsoft.com/.default",
            },
        )
        r.raise_for_status()
        payload = r.json()
        self._token = payload["access_token"]
        self._token_expires_at = time.monotonic() + int(payload.get("expires_in", 3600))
        return self._token

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        token = await self._access_token()
        r = await self._http.get(
            url, headers={"Authorization": f"Bearer {token}"}, **kwargs
        )
        r.raise_for_status()
        return r

    async def list_documents(self) -> AsyncIterator[RemoteDocument]:
        url = f"{GRAPH}/drives/{self.drive_id}/root/delta"
        while url:
            payload = (await self._get(url)).json()
            for item in payload.get("value", []):
                if "file" not in item or "deleted" in item:
                    continue
                name = item.get("name", "")
                if PurePosixPath(name).suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue
                parent = item.get("parentReference", {}).get("path", "")
                yield RemoteDocument(
                    external_id=str(item["id"]),
                    uri=item.get("webUrl", ""),
                    version=str(item.get("eTag") or item.get("cTag") or ""),
                    title=name,
                    mime_type=item.get("file", {}).get("mimeType"),
                    meta={"name": name, "path": parent},
                )
            url = payload.get("@odata.nextLink")  # deltaLink beendet die Schleife

    async def fetch(self, doc: RemoteDocument) -> ParsedDocument:
        r = await self._get(f"{GRAPH}/drives/{self.drive_id}/items/{doc.external_id}/content")
        return parse_bytes(doc.meta.get("name", doc.title or ""), r.content)

    async def aclose(self) -> None:
        if self._owns_http:
            await self._http.aclose()
