"""Dateisystem-Konnektor (v1, AP 1.2): SMB-/NFS-Mounts, lokale Verzeichnisse.

Konnektor-Vertrag (gilt auch für SharePoint/Confluence/IMAP in Phase 3):
scan() liefert alle aktuell existierenden Objekte; Change Detection läuft
zweistufig über (mtime, size) und erst bei Abweichung über den Content-Hash.
"""

import fnmatch
import hashlib
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from ..parsing import SUPPORTED_EXTENSIONS


def acl_for(relpath: str, rules: list[dict], default: list[str]) -> list[str]:
    """Pfadregel-ACLs (AP 2.2): erste passende Regel gewinnt, sonst Default.

    Regeln in sources.config: {"acl_rules": [{"pattern": "hr/*", "groups": ["hr"]}]}.
    Muster sind fnmatch-Globs relativ zur Quellwurzel; '*' überspannt dabei auch
    Verzeichnisgrenzen. Natives NTFS-/Quellrechte-Mapping bleibt Phase-2-Rest
    und dockt an derselben Stelle an.
    """
    normalized = relpath.replace("\\", "/")
    for rule in rules:
        if fnmatch.fnmatch(normalized, rule.get("pattern", "")):
            return list(rule.get("groups", default))
    return list(default)

_MIME_BY_SUFFIX = {
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".txt": "text/plain",
    ".html": "text/html",
    ".htm": "text/html",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@dataclass
class ScannedFile:
    external_id: str  # Pfad relativ zur Quellwurzel
    path: Path
    mtime: float
    size: int

    @property
    def uri(self) -> str:
        return self.path.as_uri()

    @property
    def mime_type(self) -> str | None:
        return _MIME_BY_SUFFIX.get(self.path.suffix.lower())

    @property
    def meta(self) -> dict:
        return {"mtime": self.mtime, "size": self.size}


class FilesystemConnector:
    def __init__(self, root: Path) -> None:
        self.root = root

    def scan(self) -> Iterator[ScannedFile]:
        if not self.root.is_dir():
            raise FileNotFoundError(f"Quellpfad nicht gefunden: {self.root}")
        for path in sorted(self.root.rglob("*")):
            if not path.is_file():
                continue
            if any(part.startswith(".") for part in path.relative_to(self.root).parts):
                continue  # versteckte Dateien/Verzeichnisse
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            stat = path.stat()
            yield ScannedFile(
                external_id=str(path.relative_to(self.root)),
                path=path,
                mtime=stat.st_mtime,
                size=stat.st_size,
            )

    @staticmethod
    def content_hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for block in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()
