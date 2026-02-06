"""Metadata extraction from documents."""

from __future__ import annotations

import re
from pathlib import Path


class MetadataExtractor:
    def extract(self, text: str, source_uri: str, source_type: str) -> dict:
        metadata: dict = {
            "source_type": source_type,
            "source_uri": source_uri,
            "char_count": len(text),
            "word_count": len(text.split()),
        }

        # Extract title from common patterns
        if source_type == "markdown":
            match = re.match(r"^#\s+(.+)$", text, re.MULTILINE)
            if match:
                metadata["title"] = match.group(1).strip()
        elif source_type in ("pdf", "docx"):
            path = Path(source_uri)
            metadata["title"] = path.stem.replace("-", " ").replace("_", " ").title()
            metadata["filename"] = path.name

        # Count headings (rough structure indicator)
        headings = re.findall(r"^#{1,6}\s+.+$", text, re.MULTILINE)
        metadata["heading_count"] = len(headings)

        return metadata
