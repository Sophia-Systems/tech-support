"""Document repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def get(self, doc_id: uuid.UUID) -> Document | None:
        return await self.session.get(Document, doc_id)

    async def get_with_chunks(self, doc_id: uuid.UUID) -> Document | None:
        stmt = (
            select(Document)
            .where(Document.id == doc_id)
            .options(selectinload(Document.chunks))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, status: str | None = None) -> list[Document]:
        stmt = select(Document).order_by(Document.created_at.desc())
        if status:
            stmt = stmt.where(Document.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self, doc_id: uuid.UUID, status: str, error_message: str | None = None
    ) -> None:
        doc = await self.get(doc_id)
        if doc:
            doc.status = status
            doc.error_message = error_message
            await self.session.flush()

    async def delete(self, doc_id: uuid.UUID) -> bool:
        doc = await self.get(doc_id)
        if doc:
            await self.session.delete(doc)
            await self.session.flush()
            return True
        return False
