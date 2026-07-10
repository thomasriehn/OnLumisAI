import asyncio
import logging
from contextlib import asynccontextmanager, suppress

import httpx
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from . import db, runtime
from .config import settings
from .llm import ModelGateway
from .mcp_server import mcp
from .retention import retention_loop
from .routers import (
    admin,
    auditlog,
    chat,
    documents,
    feedback,
    health,
    modelops,
    search,
    transcribe,
)

logger = logging.getLogger("onlumis")

mcp_http = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auth_mode == "dev":
        logger.warning(
            "AUTH_MODE=dev aktiv – Identität kommt aus Request-Headern. "
            "Nur für Entwicklung/Tests, niemals produktiv!"
        )
    pool = await db.init_pool()
    app.state.http = httpx.AsyncClient(timeout=settings.request_timeout_seconds)
    app.state.gateway = ModelGateway(app.state.http)
    runtime.set_gateway(app.state.gateway)
    retention_task = asyncio.create_task(retention_loop(pool))
    async with mcp.session_manager.run():
        yield
    retention_task.cancel()
    with suppress(asyncio.CancelledError):
        await retention_task
    runtime.set_gateway(None)
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
app.include_router(auditlog.router)
app.include_router(modelops.router)
app.include_router(documents.router)
app.include_router(transcribe.router)

app.mount("/mcp", mcp_http)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {"service": "onlumis-api", "version": app.version, "docs": "/docs"}
