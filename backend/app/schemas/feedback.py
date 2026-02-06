"""Feedback schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    message_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=2000)


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    message_id: uuid.UUID
    rating: int
    comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
