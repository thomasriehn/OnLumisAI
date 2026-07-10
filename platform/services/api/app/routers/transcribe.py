"""Spracheingabe/Transkription über lokales Whisper (vLLM, OpenAI-kompatibel).

Nicht konfiguriert (TRANSCRIBE_BASE_URL leer) => 501, die UI blendet die
Funktion dann aus. Audio verlässt das Haus nie – bewusst kein Browser-
Speech-API-Einsatz (der würde Audio an Cloud-Dienste senden).
"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile

from .. import audit, db
from ..auth import User, ensure_scope
from ..config import settings
from ..rate import rate_limited_user

router = APIRouter(prefix="/v1", tags=["transcribe"])


@router.post("/transcriptions")
async def transcribe(
    file: UploadFile,
    request: Request,
    user: User = Depends(rate_limited_user),
) -> dict:
    ensure_scope(user, "chat")
    if not settings.transcribe_base_url:
        raise HTTPException(status_code=501, detail="Transkription nicht konfiguriert")

    data = await file.read()
    if len(data) > settings.transcribe_max_bytes:
        raise HTTPException(status_code=413, detail="Aufnahme zu groß")

    http = request.app.state.http
    r = await http.post(
        f"{settings.transcribe_base_url}/audio/transcriptions",
        files={"file": (file.filename or "audio.webm", data, file.content_type or "audio/webm")},
        data={"model": settings.transcribe_model, "language": settings.transcribe_language},
    )
    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Whisper-Fehler ({r.status_code})")
    text = r.json().get("text", "")

    async with db.pool().acquire() as conn:
        # Bewusst ohne Inhalt: nur dass transkribiert wurde (A7/Datenschutz)
        await audit.log_event(
            conn, user.username, "transcribe", meta={"bytes": len(data)}
        )
    return {"text": text}
