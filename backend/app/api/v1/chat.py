"""Chat streaming endpoint."""

from __future__ import annotations

import json
import uuid

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.db.engine import get_db
from app.db.repositories.session_repo import SessionRepository
from app.dependencies import get_rag_pipeline
from app.schemas.chat import ChatRequest
from app.services.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/chat", tags=["chat"])
log = structlog.get_logger()


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
):
    session_repo = SessionRepository(db)

    # Create or fetch session
    if request.session_id:
        session = await session_repo.get_with_messages(request.session_id)
        if not session:
            session = await session_repo.create()
    else:
        session = await session_repo.create()

    # Save user message
    await session_repo.add_message(
        session_id=session.id, role="user", content=request.message
    )
    await db.commit()

    async def event_generator():
        try:
            result = pipeline.run(
                query=request.message,
                session_id=str(session.id),
                db=db,
            )

            async for event in result:
                yield {"event": event["event"], "data": json.dumps(event["data"])}

        except Exception as e:
            log.error("chat_stream_error", error=str(e), session_id=str(session.id))
            yield {
                "event": "error",
                "data": json.dumps({"detail": "An error occurred processing your request."}),
            }

    return EventSourceResponse(event_generator())
