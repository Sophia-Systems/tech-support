"""Feedback and escalation repositories."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import EscalationEvent, UserFeedback


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> UserFeedback:
        fb = UserFeedback(**kwargs)
        self.session.add(fb)
        await self.session.flush()
        return fb

    async def get_by_message(self, message_id: uuid.UUID) -> UserFeedback | None:
        stmt = select(UserFeedback).where(UserFeedback.message_id == message_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class EscalationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> EscalationEvent:
        event = EscalationEvent(**kwargs)
        self.session.add(event)
        await self.session.flush()
        return event

    async def list_by_session(self, session_id: uuid.UUID) -> list[EscalationEvent]:
        stmt = (
            select(EscalationEvent)
            .where(EscalationEvent.session_id == session_id)
            .order_by(EscalationEvent.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
