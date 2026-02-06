"""pgvector-backed vector store using the existing DocumentChunk table."""

from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.providers.base import VectorSearchResult


class PgVectorStore:
    def __init__(self, dsn: str):
        self._engine = create_async_engine(dsn, pool_size=5)
        self._session_factory = async_sessionmaker(self._engine, class_=AsyncSession)

    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        texts: list[str],
        metadatas: list[dict[str, str | int | float | bool]],
    ) -> None:
        async with self._session_factory() as session:
            for id_, emb, txt, meta in zip(ids, embeddings, texts, metadatas):
                await session.execute(
                    text(
                        "UPDATE document_chunks SET embedding = CAST(:embedding AS vector) WHERE id = CAST(:id AS uuid)"
                    ),
                    {"id": id_, "embedding": str(emb)},
                )
            await session.commit()

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[VectorSearchResult]:
        embedding_str = str(query_embedding)
        async with self._session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT CAST(id AS text), text, metadata,"
                    " 1 - (embedding <=> CAST(:embedding AS vector)) AS score"
                    " FROM document_chunks"
                    " WHERE embedding IS NOT NULL"
                    " ORDER BY embedding <=> CAST(:embedding AS vector)"
                    " LIMIT :top_k"
                ),
                {"embedding": embedding_str, "top_k": top_k},
            )
            rows = result.fetchall()
            return [
                VectorSearchResult(
                    chunk_id=str(row[0]),
                    text=row[1],
                    metadata=row[2] or {},
                    score=float(row[3]),
                )
                for row in rows
            ]

    async def delete(self, ids: list[str]) -> None:
        async with self._session_factory() as session:
            await session.execute(
                text(
                    "UPDATE document_chunks SET embedding = NULL WHERE CAST(id AS text) = ANY(:ids)"
                ),
                {"ids": ids},
            )
            await session.commit()
