"""Einfaches Rate-Limiting pro Nutzer (AP 2.5): Sliding Window, in-memory.

Bewusst pro Prozess gehalten (Single-Node-Appliance); bei Mehrinstanz-Betrieb
auf Redis umstellen.
"""

import asyncio
import time
from collections import deque

from fastapi import Depends, HTTPException

from .auth import User, get_current_user
from .config import settings

_WINDOW_SECONDS = 60.0
_buckets: dict[str, deque[float]] = {}
_lock = asyncio.Lock()


async def rate_limited_user(user: User = Depends(get_current_user)) -> User:
    limit = settings.rate_limit_per_minute
    if limit <= 0:
        return user
    now = time.monotonic()
    async with _lock:
        bucket = _buckets.setdefault(user.username, deque())
        while bucket and now - bucket[0] > _WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate-Limit erreicht ({limit}/min) – bitte kurz warten",
            )
        bucket.append(now)
    return user
