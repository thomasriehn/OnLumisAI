"""Deterministische Modell-Fakes für Integrationstests (ohne GPU/LLM).

Der Fake-Embedder projiziert Texte auf Schlüsselwort-Dimensionen. Damit
verhält sich die Vektorsuche semantisch nachvollziehbar: Eine Frage zu
"Sonderurlaub" landet im Urlaubs-Dokument, eine zu "Hydraulik" im
Wartungs-Dokument – über die echte pgvector-Cosine-Distanz.
"""

import hashlib
import math

DIM = 1024  # muss vector(1024) im Schema entsprechen

_KEYWORDS = {
    "urlaub": 0,
    "sonderurlaub": 1,
    "hochzeit": 2,
    "presse": 3,
    "hydraulik": 4,
    "wartung": 5,
    "filter": 6,
    "druck": 7,
}


def fake_embedding(text: str) -> list[float]:
    vec = [0.0] * DIM
    lowered = text.lower()
    for keyword, dim in _KEYWORDS.items():
        count = lowered.count(keyword)
        if count:
            vec[dim] = float(count)
    if not any(vec):
        # Kein Schlüsselwort: deterministische "Rest"-Dimension aus dem Hash
        h = int(hashlib.sha256(lowered.encode()).hexdigest(), 16)
        vec[16 + h % 64] = 1.0
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec]


class FakeEmbedder:
    """Duck-typed Ersatz für worker.embedder.Embedder / ModelGateway.embed."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [fake_embedding(t) for t in texts]


class FakeGateway(FakeEmbedder):
    """Duck-typed Ersatz für app.llm.ModelGateway (Retrieval + Chat)."""

    rerank_enabled = False

    def __init__(self, answer: str = "Laut Richtlinie gilt: ein Tag Sonderurlaub [1]."):
        self.answer = answer
        self.chat_calls: list[list[dict]] = []

    async def rerank(self, query, documents, top_n):
        return None  # wie "kein Reranker konfiguriert"

    async def chat(self, messages, **overrides):
        self.chat_calls.append(messages)
        return self.answer

    async def chat_stream(self, messages, **overrides):
        self.chat_calls.append(messages)
        for word in self.answer.split(" "):
            yield word + " "
