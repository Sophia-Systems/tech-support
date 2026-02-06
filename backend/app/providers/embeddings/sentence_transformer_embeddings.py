"""Local sentence-transformers embedding provider (for air-gapped deployments)."""

from __future__ import annotations

import asyncio
from functools import lru_cache


class SentenceTransformerEmbeddingProvider:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        self._model_name = model_name
        self._dimension = dimension
        self._model = None

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        model = self._get_model()
        embeddings = await asyncio.to_thread(model.encode, texts, normalize_embeddings=True)
        return embeddings.tolist()

    async def embed_query(self, text: str) -> list[float]:
        results = await self.embed_texts([text])
        return results[0]
