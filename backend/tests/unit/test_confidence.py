"""Tests for confidence scoring and tier classification."""

from app.core.config import ConfidenceConfig
from app.providers.base import RerankResult
from app.services.confidence import ConfidenceScorer, ConfidenceTier


def _make_scorer(**overrides) -> ConfidenceScorer:
    return ConfidenceScorer(ConfidenceConfig(overrides))


def _result(score: float, text: str = "some text") -> RerankResult:
    return RerankResult(index=0, score=score, text=text)


class TestConfidenceScorer:
    def test_empty_results_returns_off_topic(self):
        scorer = _make_scorer()
        result = scorer.score([])
        assert result.tier == ConfidenceTier.OFF_TOPIC
        assert result.top_score == 0.0

    def test_high_score_returns_answer(self):
        scorer = _make_scorer()
        result = scorer.score([_result(0.92), _result(0.85)])
        assert result.tier == ConfidenceTier.ANSWER

    def test_moderate_score_returns_caveat(self):
        scorer = _make_scorer()
        result = scorer.score([_result(0.70), _result(0.40)])
        assert result.tier == ConfidenceTier.CAVEAT

    def test_low_score_returns_decline(self):
        scorer = _make_scorer()
        result = scorer.score([_result(0.40), _result(0.30)])
        assert result.tier == ConfidenceTier.DECLINE

    def test_very_low_score_returns_escalate(self):
        scorer = _make_scorer()
        result = scorer.score([_result(0.20), _result(0.15)])
        assert result.tier == ConfidenceTier.ESCALATE

    def test_below_minimum_returns_off_topic(self):
        scorer = _make_scorer()
        result = scorer.score([_result(0.10)])
        assert result.tier == ConfidenceTier.OFF_TOPIC

    def test_custom_thresholds(self):
        scorer = _make_scorer(answer_threshold=0.95, caveat_threshold=0.80)
        result = scorer.score([_result(0.90), _result(0.50)])
        assert result.tier == ConfidenceTier.CAVEAT
