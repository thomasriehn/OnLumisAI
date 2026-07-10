from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://onlumis:onlumis@localhost:5432/onlumis"
    embeddings_base_url: str = "http://localhost:8002/v1"
    embeddings_model: str = "embed"
    embed_batch_size: int = 32
    sync_interval_seconds: int = 900
    request_timeout_seconds: float = 300.0

    # Chunking (Architektur §6.5): 300–800 Tokens ≈ 1200–3200 Zeichen
    chunk_target_chars: int = 2000
    chunk_max_chars: int = 3200
    chunk_overlap_chars: int = 200
    chunk_min_chars: int = 20


settings = Settings()
