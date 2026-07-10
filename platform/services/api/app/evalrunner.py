"""Eval-Harness (AP 5.1): goldene Fragen als Qualitäts-Gate.

Metriken je Frage:
- retrieval_hit: erwartete Quelle taucht in den Zitaten auf
- keywords_hit:  alle erwarteten Schlüsselbegriffe stehen in der Antwort
- judge_score:   optionaler LLM-as-Judge (0..1), lokal über das Chat-Modell

Läuft nightly, vor jedem Modell-/Adapter-/Prompt-Rollout (Architektur §6.7)
und auf Abruf über POST /v1/admin/evals/run.
"""

import json
import logging
import time
from uuid import UUID

import asyncpg

from .config import settings
from .rag import build_messages, mark_used_citations
from .retrieval import retrieve

logger = logging.getLogger("onlumis.eval")

JUDGE_PROMPT = """\
Du bewertest die Antwort eines Wissensassistenten. Frage:
{question}

Antwort:
{answer}

Bewerte NUR, ob die Antwort durch die Zitate gestützt, in sich konsistent und
sprachlich brauchbar (Deutsch) ist. Antworte AUSSCHLIESSLICH mit einer Zahl
zwischen 0.0 (unbrauchbar) und 1.0 (einwandfrei).\
"""


async def _judge(gateway, question: str, answer: str) -> float | None:
    try:
        raw = await gateway.chat(
            [{"role": "user", "content": JUDGE_PROMPT.format(question=question, answer=answer)}],
            temperature=0.0,
            max_tokens=8,
        )
        return max(0.0, min(1.0, float(raw.strip().split()[0].replace(",", "."))))
    except Exception:  # noqa: BLE001 - Judge ist optional, nie blockierend
        return None


async def run_eval(
    pool: asyncpg.Pool, gateway, *, notes: str | None = None, judge: bool = False
) -> UUID:
    async with pool.acquire() as conn:
        run_id = await conn.fetchval(
            "INSERT INTO eval.runs (model, notes) VALUES ($1, $2) RETURNING id",
            settings.chat_model,
            notes,
        )
        questions = await conn.fetch(
            "SELECT * FROM eval.questions WHERE enabled ORDER BY created_at"
        )

    total = retrieval_hits = keyword_hits = 0
    judge_scores: list[float] = []

    for q in questions:
        total += 1
        started = time.monotonic()
        try:
            async with pool.acquire() as conn:
                chunks = await retrieve(gateway, conn, q["question"], list(q["groups"]))
            messages, citations = build_messages(q["question"], chunks)
            answer = await gateway.chat(messages)
            citations = mark_used_citations(answer, citations)
        except Exception as exc:  # noqa: BLE001 - eine Frage stoppt den Lauf nicht
            logger.exception("Eval-Frage fehlgeschlagen: %s", q["id"])
            answer, citations = f"FEHLER: {exc}", []
        latency_ms = int((time.monotonic() - started) * 1000)

        expected_uri = q["expected_uri_substring"]
        retrieval_hit = (
            any(expected_uri in c["uri"] for c in citations) if expected_uri else True
        )
        keywords = list(q["expected_keywords"])
        keywords_hit = all(k.lower() in answer.lower() for k in keywords) if keywords else True
        judge_score = await _judge(gateway, q["question"], answer) if judge else None

        retrieval_hits += retrieval_hit
        keyword_hits += keywords_hit
        if judge_score is not None:
            judge_scores.append(judge_score)

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO eval.results
                    (run_id, question_id, retrieval_hit, keywords_hit, judge_score,
                     answer, citations, latency_ms)
                VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8)
                """,
                run_id,
                q["id"],
                retrieval_hit,
                keywords_hit,
                judge_score,
                answer,
                json.dumps(citations, ensure_ascii=False),
                latency_ms,
            )

    stats = {
        "total": total,
        "retrieval_hits": retrieval_hits,
        "keyword_hits": keyword_hits,
        "retrieval_rate": round(retrieval_hits / total, 3) if total else None,
        "keyword_rate": round(keyword_hits / total, 3) if total else None,
        "judge_avg": round(sum(judge_scores) / len(judge_scores), 3) if judge_scores else None,
    }
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE eval.runs SET finished_at = now(), stats = $2::jsonb WHERE id = $1",
            run_id,
            json.dumps(stats),
        )
    logger.info("Eval-Lauf %s abgeschlossen: %s", run_id, stats)
    return run_id
