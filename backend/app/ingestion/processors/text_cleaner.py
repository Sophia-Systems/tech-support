"""Text cleaning processor."""

from __future__ import annotations

import re


class TextCleaner:
    def clean(self, text: str) -> str:
        # Normalize whitespace
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\t", " ", text)

        # Remove excessive blank lines (keep max 2)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove excessive spaces
        text = re.sub(r" {3,}", " ", text)

        # Remove null bytes and control characters (keep newlines/tabs)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        return text.strip()
