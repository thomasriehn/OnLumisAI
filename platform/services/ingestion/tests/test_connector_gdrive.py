import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from worker.connectors.gdrive import GoogleDriveConnector


@pytest.fixture(scope="module")
def sa_key() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()


FILES = [
    {"id": "doc1", "name": "Onboarding", "mimeType": "application/vnd.google-apps.document",
     "modifiedTime": "2026-07-01T08:00:00Z", "webViewLink": "https://docs.google.com/doc1"},
    {"id": "f2", "name": "handbuch.pdf", "mimeType": "application/pdf",
     "md5Checksum": "abc123", "webViewLink": "https://drive.google.com/f2"},
    {"id": "f3", "name": "video.mp4", "mimeType": "video/mp4", "md5Checksum": "zzz"},
    {"id": "ordner", "name": "Ordner", "mimeType": "application/vnd.google-apps.folder"},
]


def _handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if "oauth2.googleapis.com/token" in url:
        return httpx.Response(200, json={"access_token": "gtok", "expires_in": 3600})
    assert request.headers.get("authorization") == "Bearer gtok"
    if url.startswith("https://www.googleapis.com/drive/v3/files?"):
        assert "'ordner-42' in parents" in request.url.params["q"]
        return httpx.Response(200, json={"files": FILES})
    if "/files/doc1/export" in url:
        assert request.url.params["mimeType"] == "text/plain"
        return httpx.Response(200, text="Erster Tag: IT-Ausstattung abholen.\n\nZweiter Tag: Schulung.")
    return httpx.Response(404)


@pytest.fixture()
def connector(sa_key):
    return GoogleDriveConnector(
        {
            "service_account_json": {
                "client_email": "bot@projekt.iam.gserviceaccount.com",
                "private_key": sa_key,
            },
            "folder_id": "ordner-42",
        },
        http=httpx.AsyncClient(transport=httpx.MockTransport(_handler)),
    )


async def test_listing_filters_and_versions(connector):
    docs = [d async for d in connector.list_documents()]
    ids = [d.external_id for d in docs]
    assert ids == ["doc1", "f2"]  # Video + Ordner gefiltert
    assert docs[0].meta["native"] is True
    assert docs[0].version.startswith("2026-07-01")  # Docs: modifiedTime
    assert docs[1].version == "abc123"               # Dateien: md5


async def test_native_doc_exported_as_text(connector):
    docs = [d async for d in connector.list_documents()]
    parsed = await connector.fetch(docs[0])
    assert parsed.title == "Onboarding"
    texts = [b.text for b in parsed.blocks]
    assert "Erster Tag: IT-Ausstattung abholen." in texts