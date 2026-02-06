"""Conversation context management for RAG pipeline."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.session_repo import SessionRepository
from app.providers.base import LLMMessage


class SessionManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SessionRepository(db)

    async def get_context_messages(
        self, session_id: str, max_turns: int = 10
    ) -> list[LLMMessage]:
        session = await self.repo.get_with_messages(uuid.UUID(session_id))
        if not session or not session.messages:
            return []

        # Take last N messages for context
        recent = session.messages[-(max_turns * 2) :]
        return [
            LLMMessage(role=msg.role, content=msg.content)
            for msg in recent
            if msg.role in ("user", "assistant")
        ]

    async def save_assistant_message(
        self,
        session_id: str,
        content: str,
        confidence_tier: str | None = None,
        sources: list[dict] | None = None,
        usage: dict | None = None,
    ) -> uuid.UUID:
        msg = await self.repo.add_message(
            session_id=uuid.UUID(session_id),
            role="assistant",
            content=content,
            confidence_tier=confidence_tier,
            sources=sources,
            usage=usage,
        )
        return msg.id
