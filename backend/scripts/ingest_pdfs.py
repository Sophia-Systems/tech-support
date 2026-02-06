"""Ingest PDF manuals from data/manuals/."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.engine import get_session_factory, dispose_engine
from app.dependencies import get_embedding_provider
from app.services.ingestion_pipeline import IngestionPipeline
from app.models.document import Document


MANUALS_DIR = Path(__file__).parent.parent.parent / "data" / "manuals"


async def main():
    settings = get_settings()
    setup_logging(settings.app.log_level)

    session_factory = get_session_factory()
    embedding_provider = get_embedding_provider()

    pdf_files = list(MANUALS_DIR.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in data/manuals/")
        return

    print(f"Found {len(pdf_files)} PDF files to ingest")

    async with session_factory() as db:
        for pdf_file in pdf_files:
            print(f"\nIngesting: {pdf_file.name}")

            doc = Document(
                title=pdf_file.stem.replace("-", " ").title(),
                source_type="pdf",
                source_uri=str(pdf_file),
                status="pending",
            )
            db.add(doc)
            await db.flush()

            pipeline = IngestionPipeline(embedding_provider=embedding_provider, db=db)
            await pipeline.ingest(str(doc.id))

            print(f"  -> {doc.chunk_count} chunks ingested")

        await db.commit()

    await dispose_engine()
    print("\nDone! PDF manuals are ready for querying.")


if __name__ == "__main__":
    asyncio.run(main())
