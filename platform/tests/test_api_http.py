"""HTTP-Level-Tests der API über ASGI (AP 2.3-ACL-Suite, API-Keys, Rate-Limit,
Audit-Export) – gegen echte pgvector-DB, Modelle gefaked.
"""

import json
from uuid import uuid4

HR = {"X-Dev-User": "hanna", "X-Dev-Groups": "hr"}
PROD = {"X-Dev-User": "paul", "X-Dev-Groups": "produktion"}
ADMIN = {"X-Dev-User": "root", "X-Dev-Groups": "all-users,onlumis-admin"}
AUDITOR = {"X-Dev-User": "dsb", "X-Dev-Groups": "onlumis-auditor"}


async def test_answers_respects_acl_and_cites(api_client):
    r = await api_client.post(
        "/v1/answers", headers=HR, json={"question": "Wie viel Sonderurlaub bei Hochzeit?"}
    )
    assert r.status_code == 200
    body = r.json()
    assert "Sonderurlaub" in body["answer"]
    uris = [c["uri"] for c in body["citations"]]
    assert any("hr/urlaub" in u for u in uris)
    assert all("prod/" not in u for u in uris)  # ACL: HR sieht keine Produktion
    assert body["citations"][0]["used"] is True


async def test_search_acl_negative(api_client):
    r = await api_client.post(
        "/v1/search", headers=PROD, json={"query": "Sonderurlaub Urlaub Hochzeit"}
    )
    assert r.status_code == 200
    assert all("hr/" not in x["uri"] for x in r.json()["results"])


async def test_api_key_lifecycle_scopes_and_acl(api_client):
    # Anlegen (nur Admin)
    r = await api_client.post(
        "/v1/admin/api-keys",
        headers=ADMIN,
        json={"name": "intranet", "scopes": ["search"], "groups": ["produktion"]},
    )
    assert r.status_code == 201
    created = r.json()
    key = created["key"]
    assert key.startswith("olk_") and created["key_prefix"] in key

    # Suche mit Key: erlaubt + ACL der Key-Gruppen (nur Produktion)
    r = await api_client.post(
        "/v1/search", headers={"X-Api-Key": key}, json={"query": "Presse Wartung Druck"}
    )
    assert r.status_code == 200
    results = r.json()["results"]
    assert results and all("prod/" in x["uri"] for x in results)

    # Chat-Scope fehlt -> 403
    r = await api_client.post(
        "/v1/answers", headers={"X-Api-Key": key}, json={"question": "Hochzeit?"}
    )
    assert r.status_code == 403

    # Admin-Endpunkte mit Key -> 403 (Keys sind nie Admin)
    r = await api_client.get(
        "/v1/admin/api-keys", headers={"X-Api-Key": key, "X-Dev-Groups": "onlumis-admin"}
    )
    assert r.status_code == 403

    # Deaktivieren -> 401 bei Nutzung; Bearer-Variante ebenfalls
    key_id = created["id"]
    r = await api_client.patch(
        f"/v1/admin/api-keys/{key_id}?enabled=false", headers=ADMIN
    )
    assert r.status_code == 200 and r.json()["enabled"] is False
    r = await api_client.post(
        "/v1/search", headers={"Authorization": f"Bearer {key}"}, json={"query": "x"}
    )
    assert r.status_code == 401

    # Ungültiger Key -> 401 (fällt nicht auf Dev-Auth zurück)
    r = await api_client.post(
        "/v1/search", headers={"X-Api-Key": "olk_falsch"}, json={"query": "x"}
    )
    assert r.status_code == 401


async def test_rate_limit(api_client, monkeypatch):
    from app.config import settings as api_settings

    monkeypatch.setattr(api_settings, "rate_limit_per_minute", 3)
    headers = {"X-Dev-User": f"limit-{uuid4().hex[:6]}", "X-Dev-Groups": "hr"}
    for _ in range(3):
        r = await api_client.post("/v1/search", headers=headers, json={"query": "urlaub"})
        assert r.status_code == 200
    r = await api_client.post("/v1/search", headers=headers, json={"query": "urlaub"})
    assert r.status_code == 429


async def test_audit_export_roles_and_formats(api_client):
    await api_client.post("/v1/search", headers=HR, json={"query": "Sonderurlaub"})

    r = await api_client.get("/v1/audit/events", headers=HR)
    assert r.status_code == 403  # normale Nutzer sehen kein Audit-Log

    r = await api_client.get("/v1/audit/events?action=search", headers=AUDITOR)
    assert r.status_code == 200
    events = r.json()["events"]
    assert events and events[0]["actor"] == "hanna"
    assert events[0]["question"] is None and events[0]["question_hash"]

    r = await api_client.get("/v1/audit/events?format=csv", headers=AUDITOR)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert r.text.splitlines()[0].startswith("id,ts,actor,action")


async def test_chat_completions_persist_roundtrip(api_client):
    r = await api_client.post(
        "/v1/chat/completions",
        headers=HR,
        json={
            "messages": [{"role": "user", "content": "Sonderurlaub bei Hochzeit?"}],
            "stream": False,
            "metadata": {"persist": True},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["choices"][0]["message"]["content"].startswith("Laut Richtlinie")
    ids = body["onlumis"]
    assert ids["message_id"] and ids["conversation_id"]

    # Feedback auf die persistierte Antwort
    r = await api_client.post(
        "/v1/feedback",
        headers=HR,
        json={"message_id": ids["message_id"], "rating": "up"},
    )
    assert r.status_code == 204

    # Fremder Nutzer darf kein Feedback auf fremde Nachricht geben
    r = await api_client.post(
        "/v1/feedback",
        headers=PROD,
        json={"message_id": ids["message_id"], "rating": "down"},
    )
    assert r.status_code == 404

    # Konversation abrufbar, Zitate gespeichert
    r = await api_client.get(f"/v1/conversations/{ids['conversation_id']}", headers=HR)
    assert r.status_code == 200
    roles = [m["role"] for m in r.json()["messages"]]
    assert roles == ["user", "assistant"]
    assert isinstance(json.loads(json.dumps(r.json()["messages"][1]["citations"])), list)