"""Konnektor-Vertrag für Remote-Quellen (AP 3.1).

Ein Konnektor liefert in list_documents() den aktuellen Bestand als
RemoteDocument-Metadaten (billig, ohne Inhalte). Die Sync-Engine vergleicht
`version` (ETag/Änderungsnummer) mit dem gespeicherten Stand und ruft nur für
geänderte Dokumente fetch() auf. Nicht mehr gelistete Dokumente werden
tombstoned (DSGVO-Löschkonzept, §7.2).

Zugangsdaten: Werte können direkt in sources.config stehen oder – empfohlen –
per "<feld>_env" auf eine Umgebungsvariable des Ingestion-Containers verweisen
(Secrets bleiben damit außerhalb der Datenbank, vgl. §6.6).
"""

import os
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from ..parsing import ParsedDocument


def secret_from_config(config: dict, key: str) -> str:
    """Liest `key` aus der Config oder `<key>_env` aus der Umgebung."""
    if config.get(key):
        return str(config[key])
    env_name = config.get(f"{key}_env")
    if env_name and os.environ.get(env_name):
        return os.environ[env_name]
    raise ValueError(f"Konnektor-Konfiguration: '{key}' oder '{key}_env' fehlt")


@dataclass
class RemoteDocument:
    external_id: str
    uri: str
    version: str                 # ETag/Versionsnummer – ändert sich mit dem Inhalt
    title: str | None = None
    mime_type: str | None = None
    meta: dict = field(default_factory=dict)
    acl_groups: list[str] | None = None  # None => default_acl der Quelle


class RemoteConnector(ABC):
    kind: str = "abstract"

    @abstractmethod
    def list_documents(self) -> AsyncIterator[RemoteDocument]:
        """Metadaten aller aktuell existierenden Dokumente (async iterator)."""

    @abstractmethod
    async def fetch(self, doc: RemoteDocument) -> ParsedDocument:
        """Inhalt eines Dokuments laden und parsen."""

    async def aclose(self) -> None:  # optional zu überschreiben
        return None
