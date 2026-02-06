"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.engine import dispose_engine

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.app.log_level)
    log.info(
        "app_starting",
        env=settings.app.env,
        llm_model=settings.llm.model,
        embedding_model=settings.embedding.model,
    )
    yield
    await dispose_engine()
    log.info("app_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Customer Service Bot API",
        version="0.1.0",
        docs_url="/docs" if settings.app.debug else None,
        redoc_url="/redoc" if settings.app.debug else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.app.api_key:
        from app.middleware.auth import APIKeyMiddleware

        app.add_middleware(APIKeyMiddleware, api_key=settings.app.api_key)

    app.include_router(api_router)

    return app


app = create_app()
