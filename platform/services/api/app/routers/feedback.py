"""Feedback zu Antworten – Rohstoff für Eval-Set und Fine-Tuning (Phase 5)."""

from fastapi import APIRouter, Depends, HTTPException

from .. import audit, db
from ..auth import User, get_current_user
from ..schemas import FeedbackRequest

router = APIRouter(prefix="/v1", tags=["feedback"])


@router.post("/feedback", status_code=204)
async def create_feedback(
    req: FeedbackRequest, user: User = Depends(get_current_user)
) -> None:
    async with db.pool().acquire() as conn:
        owned = await conn.fetchval(
            """
            SELECT 1 FROM app.messages m
            JOIN app.conversations c ON c.id = m.conversation_id
            WHERE m.id = $1 AND c.username = $2 AND m.role = 'assistant'
            """,
            req.message_id,
            user.username,
        )
        if not owned:
            raise HTTPException(status_code=404, detail="Nachricht nicht gefunden")
        await conn.execute(
            """
            INSERT INTO app.feedback (message_id, rating, comment, username)
            VALUES ($1, $2, $3, $4)
            """,
            req.message_id,
            req.rating,
            req.comment,
            user.username,
        )
        await audit.log_event(
            conn, user.username, "feedback", meta={"message_id": str(req.message_id)}
        )
