"""Audio-Ingestion (Whisper) und /v1/transcriptions-Endpoint."""

import json

import httpx

from worker.main import sync_filesystem_source
from worker.parsing import Block, ParsedDocument

from tests.fake_models import FakeEmbedder

HR = {"X-Dev-User": "hanna", "X-Dev-Groups": "hr"}


class FakeTranscriber:
    async def transcribe(self, path):
        return ParsedDocument(
            title=path.stem,
            blocks=[Block(text=f"Transkript: Besprechung zur Wartung der Presse P-300. "
                               f"Beschlossen: Ölwechsel monatlich. ({path.name})")],
        )


async def test_audio_files_are_transcribed_and_indexed(test_pool, tmp_path):
    root = tmp_path / "meetings"
    root.mkdir()
    (root / "jourfixe.mp3").write_bytes(b"ID3fakeaudio")
    (root / "notiz.md").write_text("# Notiz\n\nText der Notiz für den Vergleich.")

    async with test_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO knowledge.sources (kind, name, config, default_acl) "
            "VALUES ('filesystem', 'meetings', $1::jsonb, '{all-users}')",
            json.dumps({"root_path": str(root)}),
        )
        source = await conn.fetchrow(
            "SELECT id, name, kind, config::text AS config, default_acl "
            "FROM knowledge.sources WHERE name='meetings'"
        )

    # Ohne Transcriber: Audio wird ignoriert, nur die Notiz indexiert
    stats = await sync_filesystem_source(test_pool, FakeEmbedder(), source)
    assert stats.indexed == 1

    # Mit Transcriber: Audio wird transkribiert und durchsuchbar
    stats = await sync_filesystem_source(
        test_pool, FakeEmbedder(), source, transcriber=FakeTranscriber()
    )
    assert stats.indexed == 1  # nur die neue Audio-Datei
    async with test_pool.acquire() as conn:
        content = await conn.fetchval(
            "SELECT c.content FROM knowledge.chunks c "
            "JOIN knowledge.documents d ON d.id = c.document_id "
            "WHERE d.external_id = 'jourfixe.mp3'"
        )
    assert "Ölwechsel monatlich" in content


async def test_transcriptions_endpoint(api_client, monkeypatch):
    from app.config import settings as api_settings
    from app.main import app

    # Nicht konfiguriert -> 501 (UI blendet Mikrofon aus)
    monkeypatch.setattr(api_settings, "transcribe_base_url", "")
    r = await api_client.post(
        "/v1/transcriptions", headers=HR,
        files={"file": ("a.webm", b"audio", "audio/webm")},
    )
    assert r.status_code == 501

    # Konfiguriert -> leitet an Whisper weiter und liefert Text
    def whisper_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/audio/transcriptions")
        return httpx.Response(200, json={"text": "Wie viel Sonderurlaub bei Hochzeit?"})

    monkeypatch.setattr(api_settings, "transcribe_base_url", "http://whisper/v1")
    old_http = app.state.http
    app.state.http = httpx.AsyncClient(transport=httpx.MockTransport(whisper_handler))
    try:
        r = await api_client.post(
            "/v1/transcriptions", headers=HR,
            files={"file": ("a.webm", b"audio", "audio/webm")},
        )
    finally:
        await app.state.http.aclose()
        app.state.http = old_http
    assert r.status_code == 200
    assert r.json()["text"].startswith("Wie viel Sonderurlaub")

    # Zu große Aufnahme -> 413
    monkeypatch.setattr(api_settings, "transcribe_max_bytes", 3)
    r = await api_client.post(
        "/v1/transcriptions", headers=HR,
        files={"file": ("a.webm", b"zulang", "audio/webm")},
    )
    assert r.status_code == 413