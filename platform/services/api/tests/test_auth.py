import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.auth import User, get_current_user
from app.config import settings


def _request(headers: dict[str, str]) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
    }
    return Request(scope)


async def test_dev_mode_reads_headers(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "dev")
    user = await get_current_user(
        _request({"X-Dev-User": "alice", "X-Dev-Groups": "hr, produktion"})
    )
    assert user == User(username="alice", groups=["hr", "produktion"])


async def test_dev_mode_defaults(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "dev")
    user = await get_current_user(_request({}))
    assert user.username == "dev"
    assert user.groups == ["all-users"]
    assert not user.is_admin


async def test_admin_flag(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "dev")
    user = await get_current_user(
        _request({"X-Dev-Groups": f"all-users,{settings.admin_group}"})
    )
    assert user.is_admin


async def test_oidc_mode_requires_bearer(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "oidc")
    with pytest.raises(HTTPException) as exc:
        await get_current_user(_request({}))
    assert exc.value.status_code == 401
