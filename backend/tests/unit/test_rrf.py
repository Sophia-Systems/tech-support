"""Tests for Reciprocal Rank Fusion."""

from app.services.rag_pipeline import reciprocal_rank_fusion


def _item(chunk_id: str, text: str = "", score: float = 0.0) -> dict:
    return {"chunk_id": chunk_id, "text": text, "score": score, "metadata": {}}


class TestReciprocalRankFusion:
    def test_empty_lists(self):
        result = reciprocal_rank_fusion()
        assert result == []

    def test_single_list(self):
        items = [_item("a"), _item("b"), _item("c")]
        result = reciprocal_rank_fusion(items)
        assert len(result) == 3
        assert result[0]["chunk_id"] == "a"

    def test_overlapping_lists_boost_shared_items(self):
        list1 = [_item("a"), _item("b"), _item("c")]
        list2 = [_item("b"), _item("a"), _item("d")]
        result = reciprocal_rank_fusion(list1, list2, k=60)

        # Both a and b appear in both lists → should be top 2
        top_ids = {r["chunk_id"] for r in result[:2]}
        assert "a" in top_ids
        assert "b" in top_ids

    def test_unique_items_preserved(self):
        list1 = [_item("a")]
        list2 = [_item("b")]
        result = reciprocal_rank_fusion(list1, list2)
        ids = {r["chunk_id"] for r in result}
        assert ids == {"a", "b"}

    def test_rrf_scores_are_positive(self):
        items = [_item("a"), _item("b")]
        result = reciprocal_rank_fusion(items)
        for r in result:
            assert r["rrf_score"] > 0
