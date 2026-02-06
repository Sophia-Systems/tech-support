"""Confidence scoring and tier classification."""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from enum import Enum

from app.core.config import ConfidenceConfig
from app.providers.base import RerankResult


class ConfidenceTier(str, Enum):
    ANSWER = "ANSWER"
    CAVEAT = "CAVEAT"
    AMBIGUOUS = "AMBIGUOUS"
    DECLINE = "DECLINE"
    ESCALATE = "ESCALATE"
    OFF_TOPIC = "OFF_TOPIC"


@dataclass
class ConfidenceResult:
    tier: ConfidenceTier
    top_score: float
    score_variance: float
    distinct_topics: int


class ConfidenceScorer:
    def __init__(self, config: ConfidenceConfig):
        self.config = config

    def score(self, reranked_results: list[RerankResult]) -> ConfidenceResult:
        if not reranked_results:
            return ConfidenceResult(
                tier=ConfidenceTier.OFF_TOPIC,
                top_score=0.0,
                score_variance=0.0,
                distinct_topics=0,
            )

        top_score = reranked_results[0].score
        scores = [r.score for r in reranked_results]

        # Check minimum relevance (off-topic)
        if top_score < self.config.minimum_relevance:
            return ConfidenceResult(
                tier=ConfidenceTier.OFF_TOPIC,
                top_score=top_score,
                score_variance=0.0,
                distinct_topics=0,
            )

        score_variance = statistics.variance(scores) if len(scores) > 1 else 1.0
        distinct_topics = self._estimate_topic_count(reranked_results)

        # Check ambiguity: multiple topics with similar scores
        if (
            top_score >= self.config.caveat_threshold
            and score_variance <= self.config.ambiguity_score_variance
            and distinct_topics > 1
        ):
            return ConfidenceResult(
                tier=ConfidenceTier.AMBIGUOUS,
                top_score=top_score,
                score_variance=score_variance,
                distinct_topics=distinct_topics,
            )

        # Standard tier classification
        if top_score >= self.config.answer_threshold:
            tier = ConfidenceTier.ANSWER
        elif top_score >= self.config.caveat_threshold:
            tier = ConfidenceTier.CAVEAT
        elif top_score >= self.config.decline_threshold:
            tier = ConfidenceTier.DECLINE
        else:
            tier = ConfidenceTier.ESCALATE

        return ConfidenceResult(
            tier=tier,
            top_score=top_score,
            score_variance=score_variance,
            distinct_topics=distinct_topics,
        )

    def _estimate_topic_count(self, results: list[RerankResult]) -> int:
        """Estimate number of distinct topics from source metadata."""
        titles = set()
        for r in results:
            # Use document title from metadata if available
            # Fall back to first 50 chars of text as rough grouping
            title = r.text[:50].split("\n")[0] if r.text else ""
            titles.add(title)
        return min(len(titles), len(results))
