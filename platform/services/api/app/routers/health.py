from fastapi import APIRouter, Response

from .. import db

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(response: Response) -> dict:
    try:
        async with db.pool().acquire() as conn:
            await conn.fetchval("SELECT 1")
    except Exception as exc:  # noqa: BLE001 - Readiness soll nie crashen
        response.status_code = 503
        return {"status": "degraded", "database": f"error: {exc}"}
    return {"status": "ok", "database": "ok"}
