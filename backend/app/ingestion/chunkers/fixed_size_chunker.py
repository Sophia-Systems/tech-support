"""Fixed-size text chunker with overlap."""

from __future__ import annotations

from app.ingestion.chunkers.base import Chunk


class FixedSizeChunker:
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        metadata = metadata or {}
        chunks = []
        start = 0
        idx = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at a sentence or paragraph boundary
            if end < len(text):
                # Look for paragraph break
                para_break = text.rfind("\n\n", start + self.chunk_size // 2, end + 100)
                if para_break > start:
                    end = para_break
                else:
                    # Look for sentence break
                    for sep in [". ", ".\n", "! ", "? "]:
                        sent_break = text.rfind(sep, start + self.chunk_size // 2, end + 50)
                        if sent_break > start:
                            end = sent_break + len(sep)
                            break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        index=idx,
                        metadata={**metadata, "char_start": start, "char_end": end},
                    )
                )
                idx += 1

            start = end - self.overlap
            if start >= len(text):
                break

        return chunks
