"""Batch-Embeddings über den OpenAI-kompatiblen vLLM-/TEI-Endpoint, mit Retry."""

import asyncio
import logging

import httpx

from .config import settings

logger = logging.getLogger("onlumis.ingestion")


class Embedder:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                r = await self._http.post(
                    f"{settings.embeddings_base_url}/embeddings",
                    json={"model": settings.embeddings_model, "input": batch},
                )
                r.raise_for_status()
                data = sorted(r.json()["data"], key=lambda d: d["index"])
                return [d["embedding"] for d in data]
            except (httpx.HTTPError, KeyError) as exc:
                last_error = exc
                wait = 2**attempt
                logger.warning("Embedding-Batch fehlgeschlagen (%s), Retry in %ss", exc, wait)
                await asyncio.sleep(wait)
        raise RuntimeError(f"Embeddings nicht erreichbar: {last_error}")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for i in range(0, len(texts), settings.embed_batch_size):
            vectors.extend(await self._embed_batch(texts[i : i + settings.embed_batch_size]))
        return vectors
