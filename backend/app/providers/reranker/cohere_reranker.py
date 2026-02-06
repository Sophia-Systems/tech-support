"""Cohere reranker provider (API-backed)."""

from __future__ import annotations

import httpx

from app.providers.base import RerankResult


class CohereReranker:
    def __init__(self, api_key: str, model: str = "rerank-english-v3.0"):
        self._api_key = api_key
        self._model = model

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int = 5,
    ) -> list[RerankResult]:
        if not documents:
            return []

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.cohere.ai/v1/rerank",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "query": query,
                    "documents": documents,
                    "top_n": top_k,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

        return [
            RerankResult(
                index=r["index"],
                score=r["relevance_score"],
                text=documents[r["index"]],
            )
            for r in data["results"]
        ]
