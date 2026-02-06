"""Core RAG pipeline orchestration.

Flow: Query → Context → Rewrite → [Semantic + Keyword] → RRF → Rerank → Confidence → Generate/Decline/Escalate
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, AsyncIterator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.providers.base import (
    EmbeddingProvider,
    KeywordSearchProvider,
    LLMMessage,
    LLMProvider,
    RerankerProvider,
    RerankResult,
    VectorStoreProvider,
)
from app.services.confidence import ConfidenceScorer, ConfidenceTier
from app.services.escalation import EscalationService
from app.services.persona import PersonaService
from app.services.session_manager import SessionManager

log = structlog.get_logger()


def reciprocal_rank_fusion(
    *result_lists: list[dict[str, Any]],
    k: int = 60,
) -> list[dict[str, Any]]:
    """Fuse multiple ranked lists using Reciprocal Rank Fusion (RRF)."""
    scores: dict[str, float] = {}
    items: dict[str, dict[str, Any]] = {}

    for result_list in result_lists:
        for rank, item in enumerate(result_list):
            chunk_id = item["chunk_id"]
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank + 1)
            items[chunk_id] = item

    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    return [{**items[cid], "rrf_score": scores[cid]} for cid in sorted_ids]


class RAGPipeline:
    def __init__(
        self,
        llm: LLMProvider,
        embeddings: EmbeddingProvider,
        vector_store: VectorStoreProvider,
        reranker: RerankerProvider,
        keyword_search: KeywordSearchProvider,
        settings: Settings,
    ):
        self.llm = llm
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.reranker = reranker
        self.keyword_search = keyword_search
        self.settings = settings
        self.confidence_scorer = ConfidenceScorer(settings.confidence)
        self.persona = PersonaService(settings.persona)

    async def run(
        self,
        query: str,
        session_id: str,
        db: AsyncSession,
    ) -> AsyncIterator[dict[str, Any]]:
        session_mgr = SessionManager(db)
        escalation_svc = EscalationService(db)

        message_id = str(uuid.uuid4())

        # 1. Get conversation context
        context_messages = await session_mgr.get_context_messages(session_id)

        # 2. Query rewrite (use LLM to improve retrieval query if conversation context exists)
        search_query = query
        if context_messages:
            search_query = await self._rewrite_query(query, context_messages)
            log.info("query_rewritten", original=query, rewritten=search_query)

        # 3. Parallel retrieval: semantic + keyword
        semantic_results, keyword_results = await asyncio.gather(
            self._semantic_search(search_query),
            self._keyword_search(search_query),
        )

        # 4. Reciprocal Rank Fusion
        fused = reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
            k=self.settings.retrieval.rrf_k,
        )

        if not fused:
            # No results at all → off-topic
            off_topic_msg = self.persona.get_off_topic_message()
            yield {"event": "metadata", "data": {"session_id": session_id, "confidence_tier": "OFF_TOPIC", "message_id": message_id}}
            yield {"event": "delta", "data": {"content": off_topic_msg}}
            yield {"event": "sources", "data": []}
            yield {"event": "done", "data": {"usage": {}}}
            await session_mgr.save_assistant_message(session_id, off_topic_msg, "OFF_TOPIC")
            await db.commit()
            return

        # 5. Rerank
        reranked = await self.reranker.rerank(
            query=search_query,
            documents=[item["text"] for item in fused[: self.settings.retrieval.rerank_top_k * 3]],
            top_k=self.settings.retrieval.rerank_top_k,
        )

        # 6. Confidence scoring
        confidence = self.confidence_scorer.score(reranked)
        log.info(
            "confidence_scored",
            tier=confidence.tier.value,
            top_score=confidence.top_score,
            variance=confidence.score_variance,
        )

        # Emit metadata event
        yield {
            "event": "metadata",
            "data": {
                "session_id": session_id,
                "confidence_tier": confidence.tier.value,
                "message_id": message_id,
            },
        }

        # 7. Route by confidence tier
        if confidence.tier == ConfidenceTier.OFF_TOPIC:
            msg = self.persona.get_off_topic_message()
            yield {"event": "delta", "data": {"content": msg}}
            yield {"event": "sources", "data": []}
            yield {"event": "done", "data": {"usage": {}}}
            await session_mgr.save_assistant_message(session_id, msg, "OFF_TOPIC")
            await db.commit()
            return

        if confidence.tier == ConfidenceTier.ESCALATE:
            msg = self.persona.get_escalation_message()
            yield {"event": "delta", "data": {"content": msg}}
            yield {"event": "sources", "data": []}
            yield {"event": "done", "data": {"usage": {}}}
            await escalation_svc.escalate(session_id, query, "low_confidence")
            await session_mgr.save_assistant_message(session_id, msg, "ESCALATE")
            await db.commit()
            return

        if confidence.tier == ConfidenceTier.DECLINE:
            msg = self.persona.get_fallback_message()
            yield {"event": "delta", "data": {"content": msg}}
            yield {"event": "sources", "data": []}
            yield {"event": "done", "data": {"usage": {}}}
            await session_mgr.save_assistant_message(session_id, msg, "DECLINE")
            await db.commit()
            return

        if confidence.tier == ConfidenceTier.AMBIGUOUS:
            # Gather topic hints from top results
            topics = list({r.text[:60].split("\n")[0] for r in reranked[:3]})
            msg = self.persona.build_ambiguity_prompt(topics)
            yield {"event": "delta", "data": {"content": msg}}
            yield {"event": "sources", "data": []}
            yield {"event": "done", "data": {"usage": {}}}
            await session_mgr.save_assistant_message(session_id, msg, "AMBIGUOUS")
            await db.commit()
            return

        # ANSWER or CAVEAT → generate with LLM
        sources = self._build_sources(reranked, fused)
        system_prompt = self.persona.build_system_prompt(
            sources=sources,
            confidence_tier=confidence.tier.value,
        )

        messages = [
            LLMMessage(role="system", content=system_prompt),
            *context_messages[-6:],  # Keep last 3 turns
            LLMMessage(role="user", content=query),
        ]

        # 8. Stream LLM response
        full_response = ""
        async for token in self.llm.stream(messages):
            full_response += token
            yield {"event": "delta", "data": {"content": token}}

        # Emit sources
        yield {
            "event": "sources",
            "data": [
                {"title": s["title"], "text": s["text"][:300], "score": s["score"]}
                for s in sources
            ],
        }

        yield {"event": "done", "data": {"usage": {}}}

        # Persist
        await session_mgr.save_assistant_message(
            session_id,
            full_response,
            confidence.tier.value,
            sources=sources,
        )
        await db.commit()

    async def _rewrite_query(self, query: str, context: list[LLMMessage]) -> str:
        """Use LLM to produce a better search query from conversation context."""
        rewrite_messages = [
            LLMMessage(
                role="system",
                content=(
                    "Rewrite the user's latest question as a standalone search query. "
                    "Incorporate relevant context from the conversation. "
                    "Output ONLY the rewritten query, nothing else."
                ),
            ),
            *context[-4:],
            LLMMessage(role="user", content=query),
        ]
        response = await self.llm.complete(rewrite_messages, max_tokens=150)
        return response.content.strip() or query

    async def _semantic_search(self, query: str) -> list[dict[str, Any]]:
        query_embedding = await self.embeddings.embed_query(query)
        results = await self.vector_store.search(
            query_embedding, top_k=self.settings.retrieval.semantic_top_k
        )
        return [
            {"chunk_id": r.chunk_id, "text": r.text, "score": r.score, "metadata": r.metadata}
            for r in results
        ]

    async def _keyword_search(self, query: str) -> list[dict[str, Any]]:
        results = await self.keyword_search.search(
            query, top_k=self.settings.retrieval.keyword_top_k
        )
        return [
            {"chunk_id": r.chunk_id, "text": r.text, "score": r.score, "metadata": r.metadata}
            for r in results
        ]

    def _build_sources(
        self, reranked: list[RerankResult], fused: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Build source list from reranked results with metadata from fused results."""
        fused_by_text = {item["text"][:100]: item for item in fused}
        sources = []
        for r in reranked:
            fused_item = fused_by_text.get(r.text[:100], {})
            metadata = fused_item.get("metadata", {})
            sources.append({
                "title": metadata.get("title", "Document"),
                "text": r.text,
                "score": r.score,
                "url": metadata.get("source_uri", ""),
            })
        return sources
