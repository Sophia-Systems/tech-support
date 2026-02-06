"""Tests for chunking strategies."""

from app.ingestion.chunkers.fixed_size_chunker import FixedSizeChunker


class TestFixedSizeChunker:
    def test_short_text_single_chunk(self):
        chunker = FixedSizeChunker(chunk_size=500)
        chunks = chunker.chunk("Hello world")
        assert len(chunks) == 1
        assert chunks[0].text == "Hello world"
        assert chunks[0].index == 0

    def test_long_text_produces_multiple_chunks(self):
        chunker = FixedSizeChunker(chunk_size=100, overlap=20)
        text = "A " * 200  # 400 chars
        chunks = chunker.chunk(text)
        assert len(chunks) > 1

    def test_chunks_have_sequential_indices(self):
        chunker = FixedSizeChunker(chunk_size=50, overlap=10)
        text = "word " * 100
        chunks = chunker.chunk(text)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_metadata_propagated(self):
        chunker = FixedSizeChunker(chunk_size=500)
        chunks = chunker.chunk("Hello", metadata={"source": "test"})
        assert chunks[0].metadata["source"] == "test"

    def test_empty_text(self):
        chunker = FixedSizeChunker(chunk_size=100)
        chunks = chunker.chunk("")
        assert len(chunks) == 0
