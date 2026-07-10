"""HTTP-Tests: Konfidenz-Kurzschluss, Prompt-Profile, Wissenslücken-Report."""

from app.rag import NO_CONTEXT_ANSWER

HR = {"X-Dev-User": "hanna", "X-Dev-Groups": "hr"}
GAST = {"X-Dev-User": "gast", "X-Dev-Groups": "gast"}
GAST2 = {"X-Dev-User": "gast2", "X-Dev-Groups": "gast"}
ADMIN = {"X-Dev-User": "root", "X-Dev-Groups": "all-users,onlumis-admin"}


async def test_no_hit_short_circuit_and_gap_logging(api_client):
    from app.main import app

    calls_before = len(app.state.gateway.chat_calls)
    r = await api_client.post(
        "/v1/answers", headers=GAST, json={"question": "Wie funktioniert Anlage XY-9?"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == NO_CONTEXT_ANSWER
    assert body["citations"] == []
    # LLM wurde nicht bemüht (kein chat-Aufruf dazugekommen)
    assert len(app.state.gateway.chat_calls) == calls_before

    # Wissenslücke wurde protokolliert und taucht im Report auf
    r = await api_client.get("/v1/admin/reports/knowledge-gaps", headers=ADMIN)
    report = r.json()
    assert report["total"] >= 1
    assert any("anlage xy-9" in g["question"] for g in report["gaps"])


async def test_gap_report_aggregates_users(api_client):
    for headers in (GAST, GAST2, GAST):
        await api_client.post(
            "/v1/search", headers=headers, json={"query": "Zolltarif Export Brasilien"}
        )
    r = await api_client.get("/v1/admin/reports/knowledge-gaps?days=7", headers=ADMIN)
    entry = next(
        g for g in r.json()["gaps"] if "zolltarif" in g["question"]
    )
    assert entry["occurrences"] == 3
    assert entry["distinct_users"] == 2

    # Kein Admin -> kein Report
    r = await api_client.get("/v1/admin/reports/knowledge-gaps", headers=HR)
    assert r.status_code == 403


async def test_prompt_profile_applied_to_system_prompt(api_client):
    from app.main import app

    r = await api_client.put(
        "/v1/admin/prompt-profiles/hr",
        headers=ADMIN,
        json={"group_name": "hr", "instructions": "Beginne Antworten mit 'Kurzfassung:'."},
    )
    assert r.status_code == 200

    await api_client.post(
        "/v1/answers", headers=HR, json={"question": "Sonderurlaub bei Hochzeit?"}
    )
    system_prompt = app.state.gateway.chat_calls[-1][0]["content"]
    assert "Kurzfassung:" in system_prompt
    assert "Zusätzliche Vorgaben" in system_prompt

    # Andere Gruppe bleibt unbeeinflusst; CRUD rund
    r = await api_client.get("/v1/admin/prompt-profiles", headers=ADMIN)
    assert r.json()[0]["group_name"] == "hr"
    r = await api_client.delete("/v1/admin/prompt-profiles/hr", headers=ADMIN)
    assert r.status_code == 204
    r = await api_client.delete("/v1/admin/prompt-profiles/hr", headers=ADMIN)
    assert r.status_code == 404