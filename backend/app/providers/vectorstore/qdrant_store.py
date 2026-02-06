"""Qdrant vector store provider (alternative to pgvector)."""

from __future__ import annotations

from app.providers.base import VectorSearchResult


class QdrantStore:
    def __init__(self, url: str = "http://localhost:6333", collection: str = "document_chunks"):
        self._url = url
        self._collection = collection
        self._client = None

    def _get_client(self):
        if self._client is None:
            from qdrant_client import AsyncQdrantClient

            self._client = AsyncQdrantClient(url=self._url)
        return self._client

    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        texts: list[str],
        metadatas: list[dict[str, str | int | float | bool]],
    ) -> None:
        from qdrant_client.models import PointStruct

        client = self._get_client()
        points = [
            PointStruct(
                id=id_,
                vector=emb,
                payload={"text": txt, **meta},
            )
            for id_, emb, txt, meta in zip(ids, embeddings, texts, metadatas)
        ]
        await client.upsert(collection_name=self._collection, points=points)

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[VectorSearchResult]:
        client = self._get_client()
        results = await client.search(
            collection_name=self._collection,
            query_vector=query_embedding,
            limit=top_k,
        )
        return [
            VectorSearchResult(
                chunk_id=str(r.id),
                score=r.score,
                text=r.payload.get("text", "") if r.payload else "",
                metadata={k: v for k, v in (r.payload or {}).items() if k != "text"},
            )
            for r in results
        ]

    async def delete(self, ids: list[str]) -> None:
        from qdrant_client.models import PointIdsList

        client = self._get_client()
        await client.delete(
            collection_name=self._collection,
            points_selector=PointIdsList(points=ids),
        )
