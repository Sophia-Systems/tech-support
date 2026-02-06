"""Document schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentUploadRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    source_type: str = Field(..., pattern=r"^(markdown|pdf|web|docx)$")
    source_uri: str = Field(..., min_length=1, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    source_type: str
    source_uri: str
    status: str
    chunk_count: int
    metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class IngestionStatusResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    chunk_count: int
    error_message: str | None = None
