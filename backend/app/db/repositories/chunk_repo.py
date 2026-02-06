"""Document chunk repository with vector and FTS search."""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(self, chunks: list[DocumentChunk]) -> None:
        self.session.add_all(chunks)
        await self.session.flush()

    async def vector_search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        document_ids: list[uuid.UUID] | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(DocumentChunk, (1 - distance).label("score"))
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance)
            .limit(top_k)
        )
        if document_ids:
            stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))
        result = await self.session.execute(stmt)
        return [(row[0], float(row[1])) for row in result.all()]

    async def fts_search(
        self,
        query: str,
        top_k: int = 10,
        document_ids: list[uuid.UUID] | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        ts_query = func.plainto_tsquery("english", query)
        rank = func.ts_rank(DocumentChunk.tsv, ts_query)
        stmt = (
            select(DocumentChunk, rank.label("score"))
            .where(DocumentChunk.tsv.op("@@")(ts_query))
            .order_by(rank.desc())
            .limit(top_k)
        )
        if document_ids:
            stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))
        result = await self.session.execute(stmt)
        return [(row[0], float(row[1])) for row in result.all()]

    async def delete_by_document(self, document_id: uuid.UUID) -> int:
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        result = await self.session.execute(stmt)
        return result.rowcount
