"""Chat session repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.session import ChatMessage, ChatSession


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> ChatSession:
        chat_session = ChatSession(**kwargs)
        self.session.add(chat_session)
        await self.session.flush()
        return chat_session

    async def get(self, session_id: uuid.UUID) -> ChatSession | None:
        return await self.session.get(ChatSession, session_id)

    async def get_with_messages(self, session_id: uuid.UUID) -> ChatSession | None:
        stmt = (
            select(ChatSession)
            .where(ChatSession.id == session_id)
            .options(selectinload(ChatSession.messages))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 50) -> list[ChatSession]:
        stmt = select(ChatSession).order_by(ChatSession.updated_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_message(self, session_id: uuid.UUID, **kwargs) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, **kwargs)
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def delete(self, session_id: uuid.UUID) -> bool:
        chat_session = await self.get(session_id)
        if chat_session:
            await self.session.delete(chat_session)
            await self.session.flush()
            return True
        return False
