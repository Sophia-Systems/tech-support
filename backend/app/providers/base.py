"""Provider protocol definitions — structural subtyping for all swappable components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import AsyncIterator, Protocol, runtime_checkable


@dataclass
class LLMMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    usage: dict[str, int] = field(default_factory=dict)
    model: str = ""


@runtime_checkable
class LLMProvider(Protocol):
    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse: ...

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    @property
    def dimension(self) -> int: ...

    async def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

    async def embed_query(self, text: str) -> list[float]: ...


@dataclass
class VectorSearchResult:
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


@runtime_checkable
class VectorStoreProvider(Protocol):
    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        texts: list[str],
        metadatas: list[dict[str, str | int | float | bool]],
    ) -> None: ...

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[VectorSearchResult]: ...

    async def delete(self, ids: list[str]) -> None: ...


@dataclass
class RerankResult:
    index: int
    score: float
    text: str


@runtime_checkable
class RerankerProvider(Protocol):
    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int = 5,
    ) -> list[RerankResult]: ...


@dataclass
class KeywordSearchResult:
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


@runtime_checkable
class KeywordSearchProvider(Protocol):
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[KeywordSearchResult]: ...

    async def index(
        self,
        chunk_id: str,
        text: str,
        metadata: dict[str, str | int | float | bool],
    ) -> None: ...
