"""Provider dependency injection wiring."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.providers.base import (
    EmbeddingProvider,
    KeywordSearchProvider,
    LLMProvider,
    RerankerProvider,
    VectorStoreProvider,
)


def get_llm_provider() -> LLMProvider:
    from app.providers.llm.litellm_provider import LiteLLMProvider

    settings = get_settings()
    return LiteLLMProvider(
        model=settings.llm.model,
        api_key=settings.llm.api_key,
        api_base=settings.llm.api_base,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
    )


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.embedding.provider == "sentence-transformers":
        from app.providers.embeddings.sentence_transformer_embeddings import (
            SentenceTransformerEmbeddingProvider,
        )

        return SentenceTransformerEmbeddingProvider(
            model_name=settings.embedding.model,
            dimension=settings.embedding.dimension,
        )
    else:
        from app.providers.embeddings.litellm_embeddings import LiteLLMEmbeddingProvider

        return LiteLLMEmbeddingProvider(
            model=settings.embedding.model,
            api_key=settings.embedding.api_key,
            dimension=settings.embedding.dimension,
        )


def get_vector_store() -> VectorStoreProvider:
    from app.providers.vectorstore.pgvector_store import PgVectorStore

    settings = get_settings()
    return PgVectorStore(dsn=settings.postgres.async_url)


def get_reranker() -> RerankerProvider:
    settings = get_settings()
    if settings.reranker.provider == "cohere":
        from app.providers.reranker.cohere_reranker import CohereReranker

        return CohereReranker(api_key=settings.reranker.api_key)
    else:
        from app.providers.reranker.cross_encoder_reranker import CrossEncoderReranker

        return CrossEncoderReranker(model_name=settings.reranker.model)


def get_keyword_search() -> KeywordSearchProvider:
    from app.providers.keyword_search.postgres_fts import PostgresFTSProvider

    settings = get_settings()
    return PostgresFTSProvider(dsn=settings.postgres.async_url)


def get_rag_pipeline():
    from app.services.rag_pipeline import RAGPipeline

    settings = get_settings()
    return RAGPipeline(
        llm=get_llm_provider(),
        embeddings=get_embedding_provider(),
        vector_store=get_vector_store(),
        reranker=get_reranker(),
        keyword_search=get_keyword_search(),
        settings=settings,
    )
