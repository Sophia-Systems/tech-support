"""Voice-optimized streaming endpoint with sentence buffering."""

from __future__ import annotations

import json
import re

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.db.engine import get_db
from app.db.repositories.session_repo import SessionRepository
from app.dependencies import get_rag_pipeline
from app.schemas.chat import ChatRequest
from app.services.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/voice", tags=["voice"])
log = structlog.get_logger()

SENTENCE_ENDINGS = re.compile(r"[.!?]\s+")


@router.post("/stream")
async def voice_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
):
    session_repo = SessionRepository(db)

    if request.session_id:
        session = await session_repo.get_with_messages(request.session_id)
        if not session:
            session = await session_repo.create()
    else:
        session = await session_repo.create()

    await session_repo.add_message(
        session_id=session.id, role="user", content=request.message
    )
    await db.commit()

    async def event_generator():
        buffer = ""
        try:
            result = pipeline.run(
                query=request.message,
                session_id=str(session.id),
                db=db,
            )

            async for event in result:
                if event["event"] == "delta":
                    buffer += event["data"].get("content", "")
                    # Flush complete sentences
                    while True:
                        match = SENTENCE_ENDINGS.search(buffer)
                        if not match:
                            break
                        end = match.end()
                        sentence = buffer[:end].strip()
                        buffer = buffer[end:]
                        if sentence:
                            yield {
                                "event": "sentence",
                                "data": json.dumps({"text": sentence}),
                            }
                elif event["event"] == "metadata":
                    yield {"event": "metadata", "data": json.dumps(event["data"])}
                elif event["event"] in ("sources", "done"):
                    # Flush remaining buffer
                    if buffer.strip():
                        yield {
                            "event": "sentence",
                            "data": json.dumps({"text": buffer.strip()}),
                        }
                        buffer = ""
                    yield {"event": event["event"], "data": json.dumps(event["data"])}

        except Exception as e:
            log.error("voice_stream_error", error=str(e))
            if buffer.strip():
                yield {"event": "sentence", "data": json.dumps({"text": buffer.strip()})}
            yield {
                "event": "error",
                "data": json.dumps({"detail": "An error occurred."}),
            }

    return EventSourceResponse(event_generator())
