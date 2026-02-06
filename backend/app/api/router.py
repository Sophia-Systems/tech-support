"""Top-level API router aggregating all v1 routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import admin, chat, documents, feedback, health, sessions, voice

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(voice.router)
api_router.include_router(sessions.router)
api_router.include_router(documents.router)
api_router.include_router(feedback.router)
api_router.include_router(admin.router)
