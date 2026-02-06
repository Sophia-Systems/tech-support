"""Markdown document loader."""

from __future__ import annotations

import re

from app.ingestion.loaders.base import LoadedDocument
from app.ingestion.loaders.path_validator import validate_file_path


class MarkdownLoader:
    @property
    def supported_extensions(self) -> list[str]:
        return [".md", ".markdown"]

    def load(self, source_uri: str) -> list[LoadedDocument]:
        path = validate_file_path(source_uri)
        if not path.exists():
            raise FileNotFoundError(f"Markdown file not found: {source_uri}")

        text = path.read_text(encoding="utf-8")

        # Extract title from first H1
        title_match = re.match(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else path.stem

        return [
            LoadedDocument(
                text=text,
                metadata={"title": title, "source_type": "markdown", "filename": path.name},
                source_uri=source_uri,
            )
        ]
