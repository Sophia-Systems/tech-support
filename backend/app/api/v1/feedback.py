"""Feedback endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.db.repositories.feedback_repo import FeedbackRepository
from app.schemas.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = FeedbackRepository(db)
    fb = await repo.create(
        message_id=request.message_id,
        rating=request.rating,
        comment=request.comment,
    )
    return fb
