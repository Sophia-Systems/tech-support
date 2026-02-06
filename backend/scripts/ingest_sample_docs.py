"""Ingest sample markdown docs for local testing."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.engine import get_session_factory, dispose_engine
from app.dependencies import get_embedding_provider
from app.services.ingestion_pipeline import IngestionPipeline
from app.models.document import Document


SAMPLE_DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "sample-docs"


async def main():
    settings = get_settings()
    setup_logging(settings.app.log_level)

    session_factory = get_session_factory()
    embedding_provider = get_embedding_provider()

    md_files = list(SAMPLE_DOCS_DIR.glob("*.md"))
    if not md_files:
        print("No markdown files found in data/sample-docs/")
        return

    print(f"Found {len(md_files)} markdown files to ingest")

    async with session_factory() as db:
        for md_file in md_files:
            print(f"\nIngesting: {md_file.name}")

            # Create document record
            doc = Document(
                title=md_file.stem.replace("-", " ").title(),
                source_type="markdown",
                source_uri=str(md_file),
                status="pending",
            )
            db.add(doc)
            await db.flush()

            # Run ingestion
            pipeline = IngestionPipeline(embedding_provider=embedding_provider, db=db)
            await pipeline.ingest(str(doc.id))

            print(f"  -> {doc.chunk_count} chunks ingested")

        await db.commit()

    await dispose_engine()
    print("\nDone! Documents are ready for querying.")


if __name__ == "__main__":
    asyncio.run(main())
