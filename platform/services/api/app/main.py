import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from . import db
from .config import settings
from .llm import ModelGateway
from .routers import admin, chat, feedback, health, search

logger = logging.getLogger("onlumis")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auth_mode == "dev":
        logger.warning(
            "AUTH_MODE=dev aktiv – Identität kommt aus Request-Headern. "
            "Nur für Entwicklung/Tests, niemals produktiv!"
        )
    await db.init_pool()
    app.state.http = httpx.AsyncClient(timeout=settings.request_timeout_seconds)
    app.state.gateway = ModelGateway(app.state.http)
    yield
    await app.state.http.aclose()
    await db.close_pool()


app = FastAPI(
    title="OnLumis API",
    description="RAG-Orchestrator der OnLumis-Plattform (dokumentierte API, A4)",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(search.router)
app.include_router(feedback.router)
app.include_router(admin.router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {"service": "onlumis-api", "version": app.version, "docs": "/docs"}
