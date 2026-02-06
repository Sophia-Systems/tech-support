"""Cross-encoder reranker using sentence-transformers (zero API cost)."""

from __future__ import annotations

import asyncio
import math

from app.providers.base import RerankResult


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self._model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self._model_name)
        return self._model

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int = 5,
    ) -> list[RerankResult]:
        if not documents:
            return []

        model = self._get_model()
        pairs = [[query, doc] for doc in documents]
        scores = await asyncio.to_thread(model.predict, pairs)

        results = [
            RerankResult(
                index=i,
                score=1.0 / (1.0 + math.exp(-float(scores[i]))),
                text=documents[i],
            )
            for i in range(len(documents))
        ]
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
