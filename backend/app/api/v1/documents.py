"""Document management endpoints."""

from __future__ import annotations

import asyncio
import re
import uuid
from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.engine import get_db
from app.db.repositories.document_repo import DocumentRepository
from app.schemas.documents import (
    DocumentResponse,
    DocumentUploadRequest,
    IngestionStatusResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])
log = structlog.get_logger()

_ALLOWED_EXTENSIONS = {".pdf", ".md", ".markdown"}


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_file(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    """Upload a file (PDF or Markdown) for ingestion."""
    settings = get_settings()
    max_bytes = settings.ingestion.max_upload_size_mb * 1024 * 1024

    # Validate extension
    filename = file.filename or "upload"
    ext = Path(filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
        )

    # Read and validate size
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=422,
            detail=f"File too large ({len(content) // 1024 // 1024}MB). Max: {settings.ingestion.max_upload_size_mb}MB",
        )

    # Determine upload directory
    base_dir = settings.ingestion.allowed_base_dir
    if not base_dir:
        raise HTTPException(status_code=500, detail="INGESTION_ALLOWED_BASE_DIR not configured")
    upload_dir = Path(base_dir) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file with UUID prefix to avoid collisions
    sanitized = re.sub(r"[^\w.\-]", "_", filename)
    dest = upload_dir / f"{uuid.uuid4().hex[:12]}_{sanitized}"
    await asyncio.to_thread(dest.write_bytes, content)

    # Determine source type from extension
    source_type = "pdf" if ext == ".pdf" else "markdown"

    repo = DocumentRepository(db)
    doc = await repo.create(
        title=Path(filename).stem,
        source_type=source_type,
        source_uri=str(dest),
        metadata_={},
        status="pending",
    )
    await db.commit()
    log.info("file_uploaded", document_id=str(doc.id), filename=filename, size=len(content))

    from app.services.ingestion_pipeline import enqueue_ingestion
    await enqueue_ingestion(str(doc.id))

    return doc


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
