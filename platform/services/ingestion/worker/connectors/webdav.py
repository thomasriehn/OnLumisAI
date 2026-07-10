"""WebDAV-Konnektor: DMS-Brücke (ELO-/d.velop-WebDAV-Gateways, Nextcloud,
Sharepoint-onprem-DAV, NAS-Freigaben über HTTP).

Config (sources.config):
    {
      "base_url": "https://dms.firma.de/webdav",
      "root_path": "Ablage/Richtlinien",              # optional
      "username": "bot",
      "password": "..." | "password_env": "WEBDAV_PASSWORD"
    }
Listing über rekursives PROPFIND (Depth: 1 – Depth: infinity verbieten viele
Server). Versionsstand: getetag, Fallback getlastmodified.
"""

import xml.etree.ElementTree as ET
from collections.abc import AsyncIterator
from pathlib import PurePosixPath
from urllib.parse import quote, unquote, urlparse

import httpx

from ..parsing import SUPPORTED_EXTENSIONS, ParsedDocument, parse_bytes
from .base import RemoteConnector, RemoteDocument, secret_from_config

_DAV = "{DAV:}"
_PROPFIND_BODY = """<?xml version="1.0" encoding="utf-8"?>
<d:propfind xmlns:d="DAV:">
  <d:prop><d:resourcetype/><d:getetag/><d:getlastmodified/><d:getcontenttype/></d:prop>
</d:propfind>"""


class WebDavConnector(RemoteConnector):
    kind = "webdav"

    def __init__(self, config: dict, http: httpx.AsyncClient | None = None) -> None:
        self.base_url = str(config["base_url"]).rstrip("/")
        self.root_path = str(config.get("root_path", "")).strip("/")
        password = secret_from_config(config, "password")
        self._http = http or httpx.AsyncClient(
            auth=httpx.BasicAuth(str(config["username"]), password), timeout=120
        )
        self._owns_http = http is None
        self._base_href = urlparse(self.base_url).path.rstrip("/")

    async def _propfind(self, rel_dir: str) -> list[dict]:
        url = f"{self.base_url}/{quote(rel_dir)}" if rel_dir else self.base_url
        r = await self._http.request(
            "PROPFIND", url, content=_PROPFIND_BODY,
            headers={"Depth": "1", "Content-Type": "application/xml"},
        )
        r.raise_for_status()
        entries = []
        for response in ET.fromstring(r.content).findall(f"{_DAV}response"):
            href = unquote(response.findtext(f"{_DAV}href", ""))
            prop = response.find(f"{_DAV}propstat/{_DAV}prop")
            if prop is None:
                continue
            is_dir = prop.find(f"{_DAV}resourcetype/{_DAV}collection") is not None
            rel = href[len(self._base_href):].strip("/") if href.startswith(self._base_href) else href.strip("/")
            entries.append({
                "rel": rel,
                "dir": is_dir,
                "etag": (prop.findtext(f"{_DAV}getetag") or "").strip('"'),
                "modified": prop.findtext(f"{_DAV}getlastmodified", ""),
            })
        return entries

    async def list_documents(self) -> AsyncIterator[RemoteDocument]:
        queue = [self.root_path]
        while queue:
            current = queue.pop(0)
            for entry in await self._propfind(current):
                if entry["rel"] == current or not entry["rel"]:
                    continue  # Eintrag des Ordners selbst
                if entry["dir"]:
                    queue.append(entry["rel"])
                    continue
                if PurePosixPath(entry["rel"]).suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue
                yield RemoteDocument(
                    external_id=entry["rel"],
                    uri=f"{self.base_url}/{quote(entry['rel'])}",
                    version=entry["etag"] or entry["modified"],
                    title=PurePosixPath(entry["rel"]).name,
                )

    async def fetch(self, doc: RemoteDocument) -> ParsedDocument:
        r = await self._http.get(f"{self.base_url}/{quote(doc.external_id)}")
        r.raise_for_status()
        return parse_bytes(doc.external_id, r.content)

    async def aclose(self) -> None:
        if self._owns_http:
            await self._http.aclose()
