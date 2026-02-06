"""Feedback and escalation models."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserFeedback(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_feedback"

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(nullable=False)  # 1 (thumbs down) or 5 (thumbs up)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (Index("ix_user_feedback_message_id", "message_id"),)


class EscalationEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "escalation_events"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    webhook_status: Mapped[int | None] = mapped_column(nullable=True)
    webhook_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (Index("ix_escalation_events_session_id", "session_id"),)
