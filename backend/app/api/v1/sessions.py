"""Session CRUD endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.db.repositories.session_repo import SessionRepository
from app.schemas.chat import ChatSessionDetailResponse, ChatSessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=ChatSessionResponse, status_code=201)
async def create_session(db: AsyncSession = Depends(get_db)):
    repo = SessionRepository(db)
    session = await repo.create()
    return session


@router.get("", response_model=list[ChatSessionResponse])
async def list_sessions(limit: int = 50, db: AsyncSession = Depends(get_db)):
    repo = SessionRepository(db)
    return await repo.list_all(limit=limit)


@router.get("/{session_id}", response_model=ChatSessionDetailResponse)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SessionRepository(db)
    session = await repo.get_with_messages(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SessionRepository(db)
    deleted = await repo.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
