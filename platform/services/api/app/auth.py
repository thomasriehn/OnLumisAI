"""Authentifizierung: Dev-Header oder Keycloak-OIDC (Architektur §6.6).

Dev-Modus (AUTH_MODE=dev): Identität kommt aus X-Dev-User/X-Dev-Groups-Headern.
Ausschließlich für Entwicklung und Tests – niemals produktiv einsetzen.

OIDC-Modus: Bearer-Token wird gegen die JWKS des Keycloak-Realms validiert
(Signatur, Issuer, Ablauf, optional Audience). Gruppen kommen aus dem
"groups"-Claim (Keycloak-Group-Mapper), Fallback: realm_access.roles.
"""

import asyncio
from dataclasses import dataclass, field

import httpx
import jwt
from fastapi import Depends, HTTPException, Request

from .config import settings


@dataclass
class User:
    username: str
    groups: list[str] = field(default_factory=list)

    @property
    def is_admin(self) -> bool:
        return settings.admin_group in self.groups


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
    if settings.auth_mode == "dev":
        return _dev_user(request)

    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Bearer-Token erforderlich")
    return await _oidc_validator().validate(auth[7:].strip())


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail=f"Rolle '{settings.admin_group}' erforderlich"
        )
    return user
