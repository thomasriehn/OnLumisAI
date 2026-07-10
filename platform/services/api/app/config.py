from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Konfiguration über Umgebungsvariablen (siehe platform/.env.example)."""

    database_url: str = "postgresql://onlumis:onlumis@localhost:5432/onlumis"

    # Auth: "dev" akzeptiert X-Dev-User/X-Dev-Groups-Header (nur Entwicklung!),
    # "oidc" validiert Keycloak-Bearer-Tokens.
    auth_mode: Literal["dev", "oidc"] = "dev"
    oidc_issuer_url: str = ""
    oidc_audience: str | None = None
    admin_group: str = "onlumis-admin"
    auditor_group: str = "onlumis-auditor"

    # Requests pro Nutzer und Minute auf Chat/Suche (0 = aus). In-Memory,
    # pro Prozess – ausreichend für den Single-Node-Appliance-Betrieb.
    rate_limit_per_minute: int = 120

    # OpenAI-kompatible Modell-Endpunkte (vLLM); RERANK_BASE_URL leer = kein Reranking.
    chat_base_url: str = "http://localhost:8001/v1"
    chat_model: str = "chat"
    embeddings_base_url: str = "http://localhost:8002/v1"
    embeddings_model: str = "embed"
    rerank_base_url: str = ""
    rerank_model: str = "rerank"
    request_timeout_seconds: float = 120.0

    # Retrieval (Architektur §6.2/§6.4)
    retrieval_candidates: int = 50  # Kandidaten je Verfahren vor Fusion/Reranking
    context_chunks: int = 8         # Chunks im LLM-Kontext
    rrf_k: int = 60                 # RRF-Konstante
    max_snippet_chars: int = 240

    # Generierung
    answer_max_tokens: int = 1024
    answer_temperature: float = 0.2
    history_messages: int = 6       # Konversationsverlauf im Prompt (Anzahl Nachrichten)

    # Query-Rewriting (AP 3.7): Folgefragen werden vor dem Retrieval mit dem
    # Konversationskontext zu einer eigenständigen Suchanfrage umformuliert.
    query_rewrite_enabled: bool = True

    # Audit: false = Fragen nur als SHA-256-Hash protokollieren (Datenschutz-Default)
    audit_log_questions: bool = False


settings = Settings()
