"""Zugriff auf die vLLM-Dienste (OpenAI-kompatibel): Chat, Embeddings, Reranking."""

import json
from collections.abc import AsyncIterator

import httpx

from .config import settings


class ModelGateway:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    # ------------------------------------------------------------ Embeddings

    async def embed(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        vectors: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            r = await self._http.post(
                f"{settings.embeddings_base_url}/embeddings",
                json={"model": settings.embeddings_model, "input": batch},
            )
            r.raise_for_status()
            data = sorted(r.json()["data"], key=lambda d: d["index"])
            vectors.extend(d["embedding"] for d in data)
        return vectors

    # ------------------------------------------------------------------ Chat

    def _chat_payload(self, messages: list[dict], **overrides) -> dict:
        payload = {
            "model": settings.chat_model,
            "messages": messages,
            "temperature": settings.answer_temperature,
            "max_tokens": settings.answer_max_tokens,
        }
        payload.update({k: v for k, v in overrides.items() if v is not None})
        return payload

    async def chat(self, messages: list[dict], **overrides) -> str:
        r = await self._http.post(
            f"{settings.chat_base_url}/chat/completions",
            json=self._chat_payload(messages, **overrides),
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"] or ""

    async def chat_stream(self, messages: list[dict], **overrides) -> AsyncIterator[str]:
        """Liefert Content-Deltas des Streams (SSE des Upstream-vLLM)."""
        payload = self._chat_payload(messages, **overrides)
        payload["stream"] = True
        async with self._http.stream(
            "POST", f"{settings.chat_base_url}/chat/completions", json=payload
        ) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data.strip() == "[DONE]":
                    break
                try:
                    delta = json.loads(data)["choices"][0]["delta"]
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
                content = delta.get("content")
                if content:
                    yield content

    # --------------------------------------------------------------- Rerank

    @property
    def rerank_enabled(self) -> bool:
        return bool(settings.rerank_base_url)

    async def rerank(
        self, query: str, documents: list[str], top_n: int
    ) -> list[tuple[int, float]] | None:
        """[(index, score)] absteigend – oder None, wenn kein Reranker konfiguriert."""
        if not self.rerank_enabled or not documents:
            return None
        r = await self._http.post(
            f"{settings.rerank_base_url}/v1/rerank",
            json={
                "model": settings.rerank_model,
                "query": query,
                "documents": documents,
                "top_n": top_n,
            },
        )
        r.raise_for_status()
        results = r.json()["results"]
        ranked = [(int(x["index"]), float(x["relevance_score"])) for x in results]
        ranked.sort(key=lambda t: t[1], reverse=True)
        return ranked[:top_n]
