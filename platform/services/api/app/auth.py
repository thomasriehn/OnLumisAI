"""Authentifizierung: API-Keys, Dev-Header oder Keycloak-OIDC (§6.6, AP 4.1).

Reihenfolge der Auflösung:
1. API-Key (X-Api-Key-Header oder "Authorization: Bearer olk_..."):
   Service-Identität mit festen Scopes und ACL-Gruppen; nie Admin/Auditor.
2. AUTH_MODE=dev: X-Dev-User/X-Dev-Groups-Header – NUR Entwicklung/Tests.
3. AUTH_MODE=oidc: Bearer-Token gegen die JWKS des Keycloak-Realms
   (Signatur, Issuer, Ablauf, optional Audience). Gruppen aus dem
   "groups"-Claim (Group-Mapper im Realm), Fallback: realm_access.roles.
"""

import asyncio
import hashlib
from dataclasses import dataclass, field

import httpx
import jwt
from fastapi import Depends, HTTPException, Request

from . import db
from .config import settings

API_KEY_PREFIX = "olk_"


@dataclass
class User:
    username: str
    groups: list[str] = field(default_factory=list)
    scopes: list[str] | None = None  # None = menschlicher Nutzer (alle Scopes)

    @property
    def is_admin(self) -> bool:
        return self.scopes is None and settings.admin_group in self.groups

    @property
    def is_auditor(self) -> bool:
        return self.scopes is None and (
            settings.auditor_group in self.groups or settings.admin_group in self.groups
        )


def ensure_scope(user: User, scope: str) -> None:
    """API-Keys dürfen nur Endpunkte ihrer Scopes nutzen; Menschen alles."""
    if user.scopes is not None and scope not in user.scopes:
        raise HTTPException(status_code=403, detail=f"API-Key ohne Scope '{scope}'")


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


async def _api_key_user(key: str) -> User:
    row = await db.pool().fetchrow(
        """
        UPDATE app.api_keys SET last_used_at = now()
        WHERE key_hash = $1 AND enabled
        RETURNING name, scopes, groups
        """,
        hash_api_key(key),
    )
    if row is None:
        raise HTTPException(status_code=401, detail="API-Key ungültig oder deaktiviert")
    return User(
        username=f"apikey:{row['name']}",
        groups=list(row["groups"]),
        scopes=list(row["scopes"]),
    )


class _OidcValidator:
    def __init__(self, issuer_url: str) -> None:
        self._issuer_url = issuer_url.rstrip("/")
        self._jwk_client: jwt.PyJWKClient | None = None
        self._lock = asyncio.Lock()

    async def _jwks(self) -> jwt.PyJWKClient:
        if self._jwk_client is None:
            async with self._lock:
                if self._jwk_client is None:
                    async with httpx.AsyncClient(timeout=10) as http:
                        r = await http.get(
                            f"{self._issuer_url}/.well-known/openid-configuration"
                        )
                        r.raise_for_status()
                        jwks_uri = r.json()["jwks_uri"]
                    self._jwk_client = jwt.PyJWKClient(jwks_uri, cache_keys=True)
        return self._jwk_client

    async def validate(self, token: str) -> User:
        client = await self._jwks()
        try:
            # PyJWKClient ist synchron (holt Keys bei Bedarf per HTTP) -> Thread.
            signing_key = await asyncio.to_thread(client.get_signing_key_from_jwt, token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                issuer=self._issuer_url,
                audience=settings.oidc_audience,
                options={"verify_aud": settings.oidc_audience is not None},
            )
        except jwt.PyJWTError as exc:
            raise HTTPException(status_code=401, detail=f"Ungültiges Token: {exc}") from exc

        groups = [g.lstrip("/") for g in claims.get("groups", [])]
        if not groups:
            groups = claims.get("realm_access", {}).get("roles", [])
        username = claims.get("preferred_username") or claims.get("sub", "unbekannt")
        return User(username=username, groups=groups)


_validator: _OidcValidator | None = None


def _oidc_validator() -> _OidcValidator:
    global _validator
    if _validator is None:
        if not settings.oidc_issuer_url:
            raise HTTPException(status_code=500, detail="OIDC_ISSUER_URL nicht konfiguriert")
        _validator = _OidcValidator(settings.oidc_issuer_url)
    return _validator


def _dev_user(request: Request) -> User:
    username = request.headers.get("x-dev-user", "dev")
    groups_raw = request.headers.get("x-dev-groups", "all-users")
    groups = [g.strip() for g in groups_raw.split(",") if g.strip()]
    return User(username=username, groups=groups)


async def get_current_user(request: Request) -> User:
    api_key = request.headers.get("x-api-key", "")
    auth = request.headers.get("authorization", "")
    bearer = auth[7:].strip() if auth.lower().startswith("bearer ") else ""

    if api_key.startswith(API_KEY_PREFIX):
        return await _api_key_user(api_key)
    if bearer.startswith(API_KEY_PREFIX):
        return await _api_key_user(bearer)

    if settings.auth_mode == "dev":
        return _dev_user(request)

    if not bearer:
        raise HTTPException(status_code=401, detail="Bearer-Token erforderlich")
    return await _oidc_validator().validate(bearer)


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail=f"Rolle '{settings.admin_group}' erforderlich"
        )
    return user


async def require_auditor(user: User = Depends(get_current_user)) -> User:
    if not user.is_auditor:
        raise HTTPException(
            status_code=403, detail=f"Rolle '{settings.auditor_group}' erforderlich"
        )
    return user
