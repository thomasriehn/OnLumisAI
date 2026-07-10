"""Audio-Transkription in der Ingestion (Wissensabdeckung): Meeting-
Mitschnitte und Sprachnotizen werden über das lokale Whisper (vLLM,
OpenAI-kompatibel) in durchsuchbaren Text überführt."""

import logging
from pathlib import Path

import httpx

from .config import settings
from .parsing import Block, ParsedDocument

logger = logging.getLogger("onlumis.ingestion")

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".webm", ".flac"}

_AUDIO_MIME = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".webm": "audio/webm",
    ".flac": "audio/flac",
}


class AudioTranscriber:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def transcribe(self, path: Path) -> ParsedDocument:
        mime = _AUDIO_MIME.get(path.suffix.lower(), "application/octet-stream")
        r = await self._http.post(
            f"{settings.transcribe_base_url}/audio/transcriptions",
            files={"file": (path.name, path.read_bytes(), mime)},
            data={
                "model": settings.transcribe_model,
                "language": settings.transcribe_language,
            },
        )
        r.raise_for_status()
        text = r.json().get("text", "").strip()
        blocks = [Block(text=f"Transkript der Aufnahme {path.name}:")]
        blocks.extend(Block(text=p.strip()) for p in text.split("\n\n") if p.strip())
        return ParsedDocument(title=path.stem, blocks=blocks)
