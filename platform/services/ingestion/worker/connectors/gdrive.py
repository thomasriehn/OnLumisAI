"""Google-Drive-/Workspace-Konnektor (A2): Service-Account mit Domain-Freigabe.

Config (sources.config):
    {
      "service_account_json": {...} | "service_account_json_env": "GDRIVE_SA",
      "folder_id": "1AbC..."        # optional: nur dieser Ordner
    }
Google-native Formate (Docs/Sheets) werden als Text exportiert, sonstige
Dateien nach Format-Filter heruntergeladen. Versionsstand: md5Checksum bzw.
modifiedTime (Docs).
"""

import json
import time
from collections.abc import AsyncIterator
from pathlib import PurePosixPath

import httpx
import jwt

from ..parsing import SUPPORTED_EXTENSIONS, ParsedDocument, parse_bytes, parse_text
from .base import RemoteConnector, RemoteDocument, secret_from_config

_API = "https://www.googleapis.com/drive/v3"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_SCOPE = "https://www.googleapis.com/auth/drive.readonly"

_EXPORTS = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}


class GoogleDriveConnector(RemoteConnector):
    kind = "gdrive"

    def __init__(self, config: dict, http: httpx.AsyncClient | None = None) -> None:
        raw = config.get("service_account_json") or json.loads(
            secret_from_config(config, "service_account_json")
        )
        self._sa = raw if isinstance(raw, dict) else json.loads(raw)
        self.folder_id = config.get("folder_id")
        self._http = http or httpx.AsyncClient(timeout=120, follow_redirects=True)
        self._owns_http = http is None
        self._token: str | None = None
        self._token_expires_at = 0.0

    async def _access_token(self) -> str:
        if self._token and time.monotonic() < self._token_expires_at - 60:
            return self._token
        now = int(time.time())
        assertion = jwt.encode(
            {
                "iss": self._sa["client_email"],
                "scope": _SCOPE,
                "aud": _TOKEN_URL,
                "iat": now,
                "exp": now + 3600,
            },
            self._sa["private_key"],
            algorithm="RS256",
        )
        r = await self._http.post(
            _TOKEN_URL,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": assertion,
            },
        )
        r.raise_for_status()
        payload = r.json()
        self._token = payload["access_token"]
        self._token_expires_at = time.monotonic() + int(payload.get("expires_in", 3600))
        return self._token

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        token = await self._access_token()
        r = await self._http.get(url, headers={"Authorization": f"Bearer {token}"}, **kwargs)
        r.raise_for_status()
        return r

    async def list_documents(self) -> AsyncIterator[RemoteDocument]:
        query = "trashed = false"
        if self.folder_id:
            query += f" and '{self.folder_id}' in parents"
        page_token: str | None = None
        while True:
            params = {
                "q": query,
                "fields": "nextPageToken,files(id,name,mimeType,modifiedTime,md5Checksum,webViewLink)",
                "pageSize": 100,
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            }
            if page_token:
                params["pageToken"] = page_token
            payload = (await self._get(f"{_API}/files", params=params)).json()
            for f in payload.get("files", []):
                mime = f.get("mimeType", "")
                native = mime in _EXPORTS
                if not native and PurePosixPath(f["name"]).suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue
                if mime == "application/vnd.google-apps.folder":
                    continue
                yield RemoteDocument(
                    external_id=f["id"],
                    uri=f.get("webViewLink", ""),
                    version=f.get("md5Checksum") or f.get("modifiedTime", ""),
                    title=f["name"],
                    mime_type=mime,
                    meta={"name": f["name"], "native": native},
                )
            page_token = payload.get("nextPageToken")
            if not page_token:
                break

    async def fetch(self, doc: RemoteDocument) -> ParsedDocument:
        if doc.meta.get("native"):
            export_mime = _EXPORTS[doc.mime_type]
            r = await self._get(
                f"{_API}/files/{doc.external_id}/export",
                params={"mimeType": export_mime},
            )
            parsed = parse_text(r.text)
            return ParsedDocument(title=doc.title, blocks=parsed.blocks)
        r = await self._get(
            f"{_API}/files/{doc.external_id}", params={"alt": "media"}
        )
        return parse_bytes(doc.meta.get("name", doc.title or ""), r.content)

    async def aclose(self) -> None:
        if self._owns_http:
            await self._http.aclose()
