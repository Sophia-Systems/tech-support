"""Semantic chunker using chonkie for intelligent boundary detection."""

from __future__ import annotations

from app.ingestion.chunkers.base import Chunk


class SemanticChunker:
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._chunker = None

    def _get_chunker(self):
        if self._chunker is None:
            from chonkie import TokenChunker

            self._chunker = TokenChunker(
                chunk_size=self.chunk_size,
                chunk_overlap=self.overlap,
            )
        return self._chunker

    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        metadata = metadata or {}
        chunker = self._get_chunker()
        chonkie_chunks = chunker.chunk(text)

        return [
            Chunk(
                text=c.text,
                index=idx,
                metadata={
                    **metadata,
                    "token_count": c.token_count,
                },
            )
            for idx, c in enumerate(chonkie_chunks)
            if c.text.strip()
        ]
