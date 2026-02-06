"""PostgreSQL full-text search provider using tsvector."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.providers.base import KeywordSearchResult


class PostgresFTSProvider:
    def __init__(self, dsn: str):
        self._engine = create_async_engine(dsn, pool_size=5)
        self._session_factory = async_sessionmaker(self._engine, class_=AsyncSession)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[KeywordSearchResult]:
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    SELECT id::text, text, metadata,
                           ts_rank(tsv, plainto_tsquery('english', :query)) AS score
                    FROM document_chunks
                    WHERE tsv @@ plainto_tsquery('english', :query)
                    ORDER BY score DESC
                    LIMIT :top_k
                """),
                {"query": query, "top_k": top_k},
            )
            rows = result.fetchall()
            return [
                KeywordSearchResult(
                    chunk_id=str(row[0]),
                    text=row[1],
                    metadata=row[2] or {},
                    score=float(row[3]),
                )
                for row in rows
            ]

    async def index(
        self,
        chunk_id: str,
        text_content: str,
        metadata: dict[str, str | int | float | bool],
    ) -> None:
        async with self._session_factory() as session:
            await session.execute(
                text("""
                    UPDATE document_chunks
                    SET tsv = to_tsvector('english', :text_content)
                    WHERE id = :chunk_id
                """),
                {"chunk_id": chunk_id, "text_content": text_content},
            )
            await session.commit()
