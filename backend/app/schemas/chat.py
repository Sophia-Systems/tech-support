"""Chat request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: uuid.UUID | None = None


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    confidence_tier: str | None = None
    sources: list[SourceInfo] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SourceInfo(BaseModel):
    title: str
    text: str
    url: str | None = None
    score: float


class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionDetailResponse(ChatSessionResponse):
    messages: list[ChatMessageResponse] = []


# Fix forward ref
ChatMessageResponse.model_rebuild()
