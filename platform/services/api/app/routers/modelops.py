"""Model-Ops-Endpunkte (Phase 5): Eval-Harness und Feedback-Kuratierung.

Feedback-Kuratierung (AP 5.2): Admins prüfen Nutzer-Feedback und geben es
frei; freigegebenes Positiv-Feedback wird als Chat-Datensatz (JSONL)
exportiert und speist die LoRA-Pipeline (finetune/).
"""

import json
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .. import audit, db
from ..auth import User, require_admin
from ..evalrunner import run_eval

router = APIRouter(prefix="/v1/admin", tags=["model-ops"])


# ------------------------------------------------------------------- Evals


class EvalQuestionCreate(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    expected_uri_substring: str | None = None
    expected_keywords: list[str] = Field(default_factory=list)
    groups: list[str] = Field(default_factory=lambda: ["all-users"])


@router.get("/evals/questions")
async def list_eval_questions(user: User = Depends(require_admin)) -> list[dict]:
    rows = await db.pool().fetch("SELECT * FROM eval.questions ORDER BY created_at")
    return [
        {
            "id": str(r["id"]),
            "question": r["question"],
            "expected_uri_substring": r["expected_uri_substring"],
            "expected_keywords": list(r["expected_keywords"]),
            "groups": list(r["groups"]),
            "enabled": r["enabled"],
        }
        for r in rows
    ]


@router.post("/evals/questions", status_code=201)
async def create_eval_question(
    req: EvalQuestionCreate, user: User = Depends(require_admin)
) -> dict:
    question_id = await db.pool().fetchval(
        """
        INSERT INTO eval.questions (question, expected_uri_substring, expected_keywords, groups)
        VALUES ($1, $2, $3, $4) RETURNING id
        """,
        req.question,
        req.expected_uri_substring,
        req.expected_keywords,
        req.groups,
    )
    return {"id": str(question_id)}


@router.delete("/evals/questions/{question_id}", status_code=204)
async def delete_eval_question(
    question_id: UUID, user: User = Depends(require_admin)
) -> None:
    deleted = await db.pool().fetchval(
        "DELETE FROM eval.questions WHERE id = $1 RETURNING id", question_id
    )
    if deleted is None:
        raise HTTPException(status_code=404, detail="Frage nicht gefunden")


@router.post("/evals/run", status_code=202)
async def trigger_eval_run(
    background: BackgroundTasks,
    request: Request,
    notes: str | None = None,
    judge: bool = False,
    wait: bool = Query(default=False, description="synchron ausführen (Tests/CI)"),
    user: User = Depends(require_admin),
) -> dict:
    gateway = request.app.state.gateway
    async with db.pool().acquire() as conn:
        await audit.log_event(conn, user.username, "admin:eval_run", meta={"judge": judge})
    if wait:
        run_id = await run_eval(db.pool(), gateway, notes=notes, judge=judge)
        return {"run_id": str(run_id), "status": "finished"}
    background.add_task(run_eval, db.pool(), gateway, notes=notes, judge=judge)
    return {"status": "started"}


@router.get("/evals/runs")
async def list_eval_runs(user: User = Depends(require_admin)) -> list[dict]:
    rows = await db.pool().fetch(
        "SELECT * FROM eval.runs ORDER BY started_at DESC LIMIT 50"
    )
    return [
        {
            "id": str(r["id"]),
            "started_at": r["started_at"].isoformat(),
            "finished_at": r["finished_at"].isoformat() if r["finished_at"] else None,
            "model": r["model"],
            "notes": r["notes"],
            "stats": json.loads(r["stats"]) if r["stats"] else None,
        }
        for r in rows
    ]


@router.get("/evals/runs/{run_id}")
async def get_eval_run(run_id: UUID, user: User = Depends(require_admin)) -> dict:
    run = await db.pool().fetchrow("SELECT * FROM eval.runs WHERE id = $1", run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Lauf nicht gefunden")
    results = await db.pool().fetch(
        """
        SELECT r.*, q.question FROM eval.results r
        JOIN eval.questions q ON q.id = r.question_id
        WHERE r.run_id = $1 ORDER BY r.id
        """,
        run_id,
    )
    return {
        "id": str(run_id),
        "stats": json.loads(run["stats"]) if run["stats"] else None,
        "results": [
            {
                "question": r["question"],
                "retrieval_hit": r["retrieval_hit"],
                "keywords_hit": r["keywords_hit"],
                "judge_score": r["judge_score"],
                "answer": r["answer"],
                "latency_ms": r["latency_ms"],
            }
            for r in results
        ],
    }


# ----------------------------------------------------------------- Feedback


@router.get("/feedback")
async def list_feedback(
    reviewed: bool | None = None,
    rating: str | None = Query(default=None, pattern="^(up|down)$"),
    limit: int = Query(default=100, ge=1, le=1000),
    user: User = Depends(require_admin),
) -> list[dict]:
    rows = await db.pool().fetch(
        """
        SELECT f.id, f.rating, f.comment, f.username, f.reviewed, f.created_at,
               m.content AS answer,
               (SELECT um.content FROM app.messages um
                 WHERE um.conversation_id = m.conversation_id
                   AND um.role = 'user' AND um.created_at <= m.created_at
                 ORDER BY um.created_at DESC LIMIT 1) AS question
        FROM app.feedback f
        JOIN app.messages m ON m.id = f.message_id
        WHERE ($1::boolean IS NULL OR f.reviewed = $1)
          AND ($2::text IS NULL OR f.rating = $2)
        ORDER BY f.created_at DESC LIMIT $3
        """,
        reviewed,
        rating,
        limit,
    )
    return [
        {
            "id": str(r["id"]),
            "rating": r["rating"],
            "comment": r["comment"],
            "username": r["username"],
            "reviewed": r["reviewed"],
            "created_at": r["created_at"].isoformat(),
            "question": r["question"],
            "answer": r["answer"],
        }
        for r in rows
    ]


@router.patch("/feedback/{feedback_id}")
async def review_feedback(
    feedback_id: UUID, reviewed: bool = True, user: User = Depends(require_admin)
) -> dict:
    updated = await db.pool().fetchval(
        "UPDATE app.feedback SET reviewed = $2 WHERE id = $1 RETURNING id",
        feedback_id,
        reviewed,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Feedback nicht gefunden")
    return {"id": str(feedback_id), "reviewed": reviewed}


@router.get("/feedback/export")
async def export_feedback_dataset(
    rating: str = Query(default="up", pattern="^(up|down)$"),
    reviewed_only: bool = True,
    user: User = Depends(require_admin),
):
    """Kuratiertes Feedback als JSONL im Chat-Format (Input für finetune/)."""
    rows = await db.pool().fetch(
        """
        SELECT m.content AS answer,
               (SELECT um.content FROM app.messages um
                 WHERE um.conversation_id = m.conversation_id
                   AND um.role = 'user' AND um.created_at <= m.created_at
                 ORDER BY um.created_at DESC LIMIT 1) AS question
        FROM app.feedback f
        JOIN app.messages m ON m.id = f.message_id
        WHERE f.rating = $1 AND (NOT $2 OR f.reviewed)
        ORDER BY f.created_at
        """,
        rating,
        reviewed_only,
    )

    def lines():
        for r in rows:
            if not r["question"]:
                continue
            yield json.dumps(
                {
                    "messages": [
                        {"role": "user", "content": r["question"]},
                        {"role": "assistant", "content": r["answer"]},
                    ]
                },
                ensure_ascii=False,
            ) + "\n"

    return StreamingResponse(
        lines(),
        media_type="application/jsonl",
        headers={"content-disposition": "attachment; filename=feedback-dataset.jsonl"},
    )
