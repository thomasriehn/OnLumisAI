from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class Citation(BaseModel):
    n: int
    title: str | None = None
    uri: str
    page: int | None = None
    heading_path: str | None = None
    snippet: str
    document_id: str
    chunk_id: int
    used: bool = False


# ------------------------------------------------------------------ /v1/answers


class AnswerRequest(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    conversation_id: UUID | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)


class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    conversation_id: UUID
    message_id: UUID
    model: str


# ------------------------------------------------------- /v1/chat/completions


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "chat"
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    # OnLumis-Erweiterung: {"rag": false} deaktiviert Retrieval für diesen Call.
    metadata: dict | None = None


# ------------------------------------------------------------------ /v1/search


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    title: str | None
    uri: str
    page: int | None
    heading_path: str | None
    snippet: str
    score: float
    document_id: str
    chunk_id: int


class SearchResponse(BaseModel):
    results: list[SearchResult]


# ---------------------------------------------------------------- /v1/feedback


class FeedbackRequest(BaseModel):
    message_id: UUID
    rating: Literal["up", "down"]
    comment: str | None = Field(default=None, max_length=4000)


# ------------------------------------------------------------------ /v1/admin


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    kind: Literal["filesystem", "confluence", "sharepoint", "imap"] = "filesystem"
    config: dict = Field(default_factory=dict)
    default_acl: list[str] = Field(default_factory=lambda: ["all-users"])
    enabled: bool = True


class SourceUpdate(BaseModel):
    config: dict | None = None
    default_acl: list[str] | None = None
    enabled: bool | None = None


class SourceOut(BaseModel):
    id: UUID
    name: str
    kind: str
    config: dict
    default_acl: list[str]
    enabled: bool
    last_sync_at: str | None = None
    last_sync_status: str | None = None
    document_count: int = 0


class StatsOut(BaseModel):
    documents: int
    chunks: int
    conversations: int
    feedback_open: int


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scopes: list[Literal["chat", "search"]] = Field(default_factory=lambda: ["chat", "search"])
    groups: list[str] = Field(default_factory=lambda: ["all-users"])


class ApiKeyOut(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    scopes: list[str]
    groups: list[str]
    enabled: bool
    created_by: str
    last_used_at: str | None = None


class ApiKeyCreated(ApiKeyOut):
    key: str  # Klartext – wird nur einmal bei der Erstellung geliefert
