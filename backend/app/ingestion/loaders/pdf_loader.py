"""PDF document loader using unstructured."""

from __future__ import annotations

from app.ingestion.loaders.base import LoadedDocument
from app.ingestion.loaders.path_validator import validate_file_path


class PDFLoader:
    @property
    def supported_extensions(self) -> list[str]:
        return [".pdf"]

    def load(self, source_uri: str) -> list[LoadedDocument]:
        path = validate_file_path(source_uri)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {source_uri}")

        from unstructured.partition.pdf import partition_pdf

        elements = partition_pdf(filename=str(path))

        text = "\n\n".join(str(el) for el in elements if str(el).strip())

        return [
            LoadedDocument(
                text=text,
                metadata={
                    "title": path.stem,
                    "source_type": "pdf",
                    "filename": path.name,
                    "page_count": _count_pages(elements),
                },
                source_uri=source_uri,
            )
        ]


def _count_pages(elements) -> int:
    pages = set()
    for el in elements:
        if hasattr(el, "metadata") and hasattr(el.metadata, "page_number"):
            pages.add(el.metadata.page_number)
    return len(pages) if pages else 1
