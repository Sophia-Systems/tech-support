"""Pinecone vector store provider (alternative to pgvector)."""

from __future__ import annotations

from app.providers.base import VectorSearchResult


class PineconeStore:
    def __init__(self, api_key: str, index_name: str = "document-chunks"):
        self._api_key = api_key
        self._index_name = index_name
        self._index = None

    def _get_index(self):
        if self._index is None:
            from pinecone import Pinecone

            pc = Pinecone(api_key=self._api_key)
            self._index = pc.Index(self._index_name)
        return self._index

    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        texts: list[str],
        metadatas: list[dict[str, str | int | float | bool]],
    ) -> None:
        index = self._get_index()
        vectors = [
            {"id": id_, "values": emb, "metadata": {"text": txt, **meta}}
            for id_, emb, txt, meta in zip(ids, embeddings, texts, metadatas)
        ]
        # Pinecone upsert in batches of 100
        for i in range(0, len(vectors), 100):
            index.upsert(vectors=vectors[i : i + 100])

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[VectorSearchResult]:
        index = self._get_index()
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_metadata,
        )
        return [
            VectorSearchResult(
                chunk_id=match["id"],
                score=match["score"],
                text=match.get("metadata", {}).get("text", ""),
                metadata={
                    k: v
                    for k, v in match.get("metadata", {}).items()
                    if k != "text"
                },
            )
            for match in results.get("matches", [])
        ]

    async def delete(self, ids: list[str]) -> None:
        index = self._get_index()
        index.delete(ids=ids)
