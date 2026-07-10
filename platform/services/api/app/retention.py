"""Aufbewahrungs-Job (Quick Win, DSGVO §6.6): löscht alte Konversationen und
Audit-Einträge nach konfigurierbaren Fristen (0 = deaktiviert)."""

import asyncio
import logging

import asyncpg

from .config import settings

logger = logging.getLogger("onlumis.retention")

_DAY_SECONDS = 24 * 3600


async def purge_once(pool: asyncpg.Pool) -> dict[str, int]:
    removed = {"conversations": 0, "audit_events": 0}
    async with pool.acquire() as conn:
        if settings.retention_days_conversations > 0:
            result = await conn.execute(
                "DELETE FROM app.conversations "
                "WHERE created_at < now() - make_interval(days => $1)",
                settings.retention_days_conversations,
            )
            removed["conversations"] = int(result.split()[-1])
        if settings.retention_days_audit > 0:
            result = await conn.execute(
                "DELETE FROM audit.events "
                "WHERE ts < now() - make_interval(days => $1)",
                settings.retention_days_audit,
            )
            removed["audit_events"] = int(result.split()[-1])
    if any(removed.values()):
        logger.info("Retention: %s", removed)
    return removed


async def retention_loop(pool: asyncpg.Pool) -> None:
    if settings.retention_days_conversations <= 0 and settings.retention_days_audit <= 0:
        return
    await asyncio.sleep(60)  # Startphase abwarten
    while True:
        try:
            await purge_once(pool)
        except Exception:  # noqa: BLE001 - Retention darf den Betrieb nie stören
            logger.exception("Retention-Lauf fehlgeschlagen")
        await asyncio.sleep(_DAY_SECONDS)
