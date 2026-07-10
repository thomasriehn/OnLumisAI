"""HTTP-Tests für Eval-Harness (AP 5.1) und Feedback-Kuratierung (AP 5.2)."""

ADMIN = {"X-Dev-User": "root", "X-Dev-Groups": "all-users,onlumis-admin"}
HR = {"X-Dev-User": "hanna", "X-Dev-Groups": "hr"}


async def test_eval_harness_end_to_end(api_client):
    # Zwei goldene Fragen: eine muss bestehen, eine muss durchfallen
    r = await api_client.post(
        "/v1/admin/evals/questions",
        headers=ADMIN,
        json={
            "question": "Wie viel Sonderurlaub bei Hochzeit?",
            "expected_uri_substring": "hr/urlaub",
            "expected_keywords": ["Sonderurlaub"],
            "groups": ["hr"],
        },
    )
    assert r.status_code == 201
    r = await api_client.post(
        "/v1/admin/evals/questions",
        headers=ADMIN,
        json={
            "question": "Wie lang ist die Kündigungsfrist?",
            "expected_uri_substring": "hr/kuendigung",   # existiert nicht
            "expected_keywords": ["Kündigungsfrist"],     # steht nicht in der Antwort
            "groups": ["produktion"],
        },
    )
    assert r.status_code == 201

    # Normale Nutzer dürfen den Eval nicht starten
    r = await api_client.post("/v1/admin/evals/run?wait=true", headers=HR)
    assert r.status_code == 403

    r = await api_client.post("/v1/admin/evals/run?wait=true", headers=ADMIN)
    assert r.status_code == 202
    run_id = r.json()["run_id"]

    r = await api_client.get("/v1/admin/evals/runs", headers=ADMIN)
    stats = r.json()[0]["stats"]
    assert stats["total"] == 2
    assert stats["retrieval_hits"] == 1 and stats["retrieval_rate"] == 0.5
    assert stats["keyword_hits"] == 1 and stats["keyword_rate"] == 0.5

    r = await api_client.get(f"/v1/admin/evals/runs/{run_id}", headers=ADMIN)
    results = r.json()["results"]
    assert len(results) == 2
    passed = next(x for x in results if "Hochzeit" in x["question"])
    failed = next(x for x in results if "Kündigungsfrist" in x["question"])
    assert passed["retrieval_hit"] and passed["keywords_hit"]
    assert not failed["retrieval_hit"] and not failed["keywords_hit"]
    assert passed["latency_ms"] >= 0


async def test_feedback_curation_and_export(api_client):
    # Nutzerin stellt Frage und bewertet die Antwort positiv
    r = await api_client.post(
        "/v1/answers", headers=HR, json={"question": "Sonderurlaub bei Hochzeit?"}
    )
    message_id = r.json()["message_id"]
    r = await api_client.post(
        "/v1/feedback",
        headers=HR,
        json={"message_id": message_id, "rating": "up", "comment": "korrekt"},
    )
    assert r.status_code == 204

    # Kuratierungs-Queue: offenes Feedback mit Frage/Antwort-Kontext
    r = await api_client.get("/v1/admin/feedback?reviewed=false", headers=ADMIN)
    queue = r.json()
    assert len(queue) == 1
    entry = queue[0]
    assert entry["question"] == "Sonderurlaub bei Hochzeit?"
    assert entry["rating"] == "up" and entry["comment"] == "korrekt"

    # Vor Freigabe: Export (reviewed_only) ist leer
    r = await api_client.get("/v1/admin/feedback/export", headers=ADMIN)
    assert r.text.strip() == ""

    # Freigeben -> Export enthält das Chat-Beispiel
    r = await api_client.patch(f"/v1/admin/feedback/{entry['id']}", headers=ADMIN)
    assert r.json()["reviewed"] is True
    r = await api_client.get("/v1/admin/feedback/export", headers=ADMIN)
    import json

    lines = [json.loads(line) for line in r.text.strip().splitlines()]
    assert len(lines) == 1
    assert lines[0]["messages"][0] == {
        "role": "user", "content": "Sonderurlaub bei Hochzeit?"
    }
    assert lines[0]["messages"][1]["role"] == "assistant"

    # Queue ist danach leer
    r = await api_client.get("/v1/admin/feedback?reviewed=false", headers=ADMIN)
    assert r.json() == []