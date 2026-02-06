"""Escalation service — webhook dispatch + event logging."""

from __future__ import annotations

import uuid

import httpx
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.repositories.feedback_repo import EscalationRepository

log = structlog.get_logger()


class EscalationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EscalationRepository(db)

    async def escalate(
        self,
        session_id: str,
        query: str,
        reason: str,
        message_id: str | None = None,
    ) -> None:
        settings = get_settings()

        webhook_status = None
        webhook_response = None

        if settings.escalation.webhook_url:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        settings.escalation.webhook_url,
                        json={
                            "session_id": session_id,
                            "query": query,
                            "reason": reason,
                        },
                        timeout=10,
                    )
                    webhook_status = resp.status_code
                    webhook_response = {"body": resp.text[:500]}
                    log.info(
                        "escalation_webhook_sent",
                        session_id=session_id,
                        status=webhook_status,
                    )
            except Exception as e:
                log.error("escalation_webhook_failed", error=str(e))
                webhook_status = 0
                webhook_response = {"error": str(e)}

        await self.repo.create(
            session_id=uuid.UUID(session_id),
            message_id=uuid.UUID(message_id) if message_id else None,
            reason=reason,
            query=query,
            webhook_status=webhook_status,
            webhook_response=webhook_response,
        )
