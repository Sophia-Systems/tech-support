"""arq background worker for document ingestion."""

from __future__ import annotations

import structlog
from arq.connections import RedisSettings

from app.core.config import get_settings
from app.db.engine import get_session_factory
from app.dependencies import get_embedding_provider
from app.services.ingestion_pipeline import IngestionPipeline

log = structlog.get_logger()


async def ingest_document(ctx: dict, document_id: str) -> None:
    """Background job: ingest a document by ID."""
    log.info("worker_ingesting", document_id=document_id)

    session_factory = get_session_factory()
    async with session_factory() as db:
        embedding_provider = get_embedding_provider()
        pipeline = IngestionPipeline(embedding_provider=embedding_provider, db=db)
        await pipeline.ingest(document_id)


async def startup(ctx: dict) -> None:
    from app.core.logging import setup_logging

    settings = get_settings()
    setup_logging(settings.app.log_level)
    log.info("worker_started")


async def shutdown(ctx: dict) -> None:
    from app.db.engine import dispose_engine

    await dispose_engine()
    log.info("worker_shutdown")


class WorkerSettings:
    functions = [ingest_document]
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 5
    job_timeout = 600  # 10 minutes for large documents

    @staticmethod
    def redis_settings() -> RedisSettings:
        settings = get_settings()
        return RedisSettings.from_dsn(settings.redis.url)
