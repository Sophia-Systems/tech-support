"""Document ingestion orchestration — load, clean, chunk, embed, index."""

from __future__ import annotations

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import IngestionError
from app.db.repositories.document_repo import DocumentRepository
from app.ingestion.chunkers.fixed_size_chunker import FixedSizeChunker
from app.ingestion.loaders.base import get_loader
from app.ingestion.processors.metadata_extractor import MetadataExtractor
from app.ingestion.processors.text_cleaner import TextCleaner
from app.models.document import DocumentChunk
from app.providers.base import EmbeddingProvider

log = structlog.get_logger()


class IngestionPipeline:
    def __init__(self, embedding_provider: EmbeddingProvider, db: AsyncSession):
        self.embedding_provider = embedding_provider
        self.db = db
        settings = get_settings()
        self.chunker = FixedSizeChunker(
            chunk_size=settings.retrieval.chunk_size,
            overlap=settings.retrieval.chunk_overlap,
        )
        self.cleaner = TextCleaner()
        self.metadata_extractor = MetadataExtractor()

    async def ingest(self, document_id: str) -> None:
        doc_repo = DocumentRepository(self.db)
        doc = await doc_repo.get(uuid.UUID(document_id))
        if not doc:
            raise IngestionError(f"Document not found: {document_id}")

        await doc_repo.update_status(doc.id, "processing")
        await self.db.commit()

        try:
            # 1. Load
            loader = get_loader(doc.source_type)
            loaded_docs = loader.load(doc.source_uri)
            log.info("documents_loaded", document_id=document_id, count=len(loaded_docs))

            all_chunks = []
            for loaded_doc in loaded_docs:
                # 2. Clean
                cleaned_text = self.cleaner.clean(loaded_doc.text)

                # 3. Extract metadata
                doc_metadata = self.metadata_extractor.extract(
                    cleaned_text, doc.source_uri, doc.source_type
                )
                doc_metadata.update(loaded_doc.metadata)

                # 4. Chunk
                chunks = self.chunker.chunk(cleaned_text, metadata=doc_metadata)
                log.info("document_chunked", document_id=document_id, chunk_count=len(chunks))

                # 5. Create chunk records
                for chunk in chunks:
                    db_chunk = DocumentChunk(
                        document_id=doc.id,
                        chunk_index=chunk.index,
                        text=chunk.text,
                        metadata_=chunk.metadata,
                    )
                    self.db.add(db_chunk)
                    all_chunks.append(db_chunk)

            await self.db.flush()

            # 6. Embed in batches
            batch_size = 100
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i : i + batch_size]
                texts = [c.text for c in batch]
                embeddings = await self.embedding_provider.embed_texts(texts)
                for chunk, embedding in zip(batch, embeddings):
                    chunk.embedding = embedding
                log.info(
                    "batch_embedded",
                    document_id=document_id,
                    batch_start=i,
                    batch_size=len(batch),
                )

            await self.db.flush()

            # 7. Build FTS index
            from sqlalchemy import text as sa_text

            for chunk in all_chunks:
                await self.db.execute(
                    sa_text(
                        "UPDATE document_chunks SET tsv = to_tsvector('english', :text) WHERE id = :id"
                    ),
                    {"text": chunk.text, "id": chunk.id},
                )

            # 8. Update document status
            doc.status = "ready"
            doc.chunk_count = len(all_chunks)
            await self.db.commit()

            log.info(
                "ingestion_complete",
                document_id=document_id,
                chunk_count=len(all_chunks),
            )

        except Exception as e:
            await self.db.rollback()
            # Re-open transaction for status update
            doc = await doc_repo.get(uuid.UUID(document_id))
            if doc:
                doc.status = "error"
                doc.error_message = str(e)
                await self.db.commit()
            log.error("ingestion_failed", document_id=document_id, error=str(e))
            raise IngestionError(str(e)) from e


async def enqueue_ingestion(document_id: str) -> None:
    """Enqueue document ingestion to the arq worker."""
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        from app.core.config import get_settings

        settings = get_settings()
        redis = await create_pool(RedisSettings.from_dsn(settings.redis.url))
        await redis.enqueue_job("ingest_document", document_id)
        log.info("ingestion_enqueued", document_id=document_id)
    except Exception as e:
        log.warning(
            "ingestion_enqueue_failed_running_inline",
            document_id=document_id,
            error=str(e),
        )
        # Fallback: run inline if Redis isn't available (dev convenience)
