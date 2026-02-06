"""LiteLLM-based embedding provider (API-backed)."""

from __future__ import annotations

import litellm


class LiteLLMEmbeddingProvider:
    def __init__(self, model: str, api_key: str, dimension: int = 1536):
        self._model = model
        self._api_key = api_key
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = await litellm.aembedding(
            model=self._model,
            input=texts,
            api_key=self._api_key,
        )
        return [item["embedding"] for item in response.data]

    async def embed_query(self, text: str) -> list[float]:
        results = await self.embed_texts([text])
        return results[0]
