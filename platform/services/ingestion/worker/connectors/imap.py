"""IMAP-Konnektor (AP 3.4): explizit freigegebene Postfächer/Ordner.

Config (sources.config):
    {
      "host": "mail.firma.de", "port": 993,
      "username": "wissen@firma.de",
      "password": "..." | "password_env": "IMAP_PASSWORD",
      "folders": ["INBOX", "Projekte"]
    }
E-Mails sind unveränderlich: external_id = Ordner/UIDVALIDITY/UID, die zugleich
als Version dient. Ändert sich die UIDVALIDITY des Ordners, wird der Bestand
neu indexiert und der alte tombstoned. imaplib ist synchron und läuft daher in
einem Thread.
"""

import email
import email.policy
import imaplib
from asyncio import to_thread
from collections.abc import AsyncIterator

from ..parsing import Block, ParsedDocument, parse_html
from .base import RemoteConnector, RemoteDocument, secret_from_config


def email_bytes_to_parsed(raw: bytes) -> tuple[ParsedDocument, dict]:
    """E-Mail → Blöcke (Betreff/Kopf + Text); reine Funktion, direkt testbar."""
    message = email.message_from_bytes(raw, policy=email.policy.default)
    subject = str(message.get("subject", "")) or None
    meta = {
        "from": str(message.get("from", "")),
        "to": str(message.get("to", "")),
        "date": str(message.get("date", "")),
    }

    body = message.get_body(preferencelist=("plain", "html"))
    blocks: list[Block] = []
    header = f"Von: {meta['from']} · An: {meta['to']} · Datum: {meta['date']}"
    blocks.append(Block(text=header))
    if body is not None:
        content = body.get_content()
        if body.get_content_type() == "text/html":
            blocks.extend(parse_html(content).blocks)
        else:
            blocks.extend(
                Block(text=p.strip()) for p in content.split("\n\n") if p.strip()
            )
    return ParsedDocument(title=subject, blocks=blocks), meta


class ImapConnector(RemoteConnector):
    kind = "imap"

    def __init__(self, config: dict) -> None:
        self.host = str(config["host"])
        self.port = int(config.get("port", 993))
        self.username = str(config["username"])
        self.password = secret_from_config(config, "password")
        self.folders: list[str] = list(config.get("folders", ["INBOX"]))
        self._client: imaplib.IMAP4_SSL | None = None

    # ------------------------------------------------------ sync (im Thread)

    def _connect(self) -> imaplib.IMAP4_SSL:
        if self._client is None:
            self._client = imaplib.IMAP4_SSL(self.host, self.port)
            self._client.login(self.username, self.password)
        return self._client

    def _list_folder(self, folder: str) -> list[tuple[str, str]]:
        client = self._connect()
        status, _ = client.select(f'"{folder}"', readonly=True)
        if status != "OK":
            raise RuntimeError(f"IMAP-Ordner nicht wählbar: {folder}")
        uidvalidity = (client.response("UIDVALIDITY")[1] or [b"0"])[0].decode()
        _, data = client.uid("search", None, "ALL")
        uids = data[0].split() if data and data[0] else []
        return [(uidvalidity, uid.decode()) for uid in uids]

    def _fetch_message(self, folder: str, uid: str) -> bytes:
        client = self._connect()
        client.select(f'"{folder}"', readonly=True)
        status, data = client.uid("fetch", uid, "(RFC822)")
        if status != "OK" or not data or data[0] is None:
            raise RuntimeError(f"IMAP-Fetch fehlgeschlagen: {folder}/{uid}")
        return data[0][1]

    def _logout(self) -> None:
        if self._client is not None:
            try:
                self._client.logout()
            finally:
                self._client = None

    # --------------------------------------------------------- Konnektor-API

    async def list_documents(self) -> AsyncIterator[RemoteDocument]:
        for folder in self.folders:
            entries = await to_thread(self._list_folder, folder)
            for uidvalidity, uid in entries:
                external_id = f"{folder}/{uidvalidity}/{uid}"
                yield RemoteDocument(
                    external_id=external_id,
                    uri=f"imap://{self.host}/{folder};UIDVALIDITY={uidvalidity};UID={uid}",
                    version=external_id,  # E-Mails sind unveränderlich
                    mime_type="message/rfc822",
                    meta={"folder": folder},
                )

    async def fetch(self, doc: RemoteDocument) -> ParsedDocument:
        folder, _, uid = doc.external_id.split("/", 2)[0], None, doc.external_id.rsplit("/", 1)[1]
        raw = await to_thread(self._fetch_message, folder, uid)
        parsed, meta = email_bytes_to_parsed(raw)
        doc.meta.update(meta)
        return parsed

    async def aclose(self) -> None:
        await to_thread(self._logout)
