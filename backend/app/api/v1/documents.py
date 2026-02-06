"""Document management endpoints."""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.db.repositories.document_repo import DocumentRepository
from app.schemas.documents import (
    DocumentResponse,
    DocumentUploadRequest,
    IngestionStatusResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])
log = structlog.get_logger()


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    request: DocumentUploadRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    doc = await repo.create(
        title=request.title,
        source_type=request.source_type,
        source_uri=request.source_uri,
        metadata_=request.metadata,
        status="pending",
    )
    log.info("document_created", document_id=str(doc.id), source_type=request.source_type)

    # Enqueue ingestion task
    from app.services.ingestion_pipeline import enqueue_ingestion

    await enqueue_ingestion(str(doc.id))

    return doc


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    return await repo.list_all(status=status)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = DocumentRepository(db)
    doc = await repo.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/status", response_model=IngestionStatusResponse)
async def get_ingestion_status(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = DocumentRepository(db)
    doc = await repo.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return IngestionStatusResponse(
        document_id=doc.id,
        status=doc.status,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = DocumentRepository(db)
    deleted = await repo.delete(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
