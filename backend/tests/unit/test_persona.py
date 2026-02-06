"""Tests for persona service."""

from app.core.config import PersonaConfig
from app.services.persona import PersonaService


def _make_persona(**overrides) -> PersonaService:
    config = PersonaConfig({
        "company_name": "TestCorp",
        "product_name": "TestDryer",
        "tone": "friendly",
        "template_path": "persona/default.yaml",
        **overrides,
    })
    return PersonaService(config)


class TestPersonaService:
    def test_system_prompt_includes_company(self):
        persona = _make_persona()
        prompt = persona.build_system_prompt(sources=[], confidence_tier="ANSWER")
        assert "TestCorp" in prompt

    def test_system_prompt_includes_sources(self):
        persona = _make_persona()
        sources = [{"title": "Manual Ch. 3", "text": "Clean the lint trap.", "score": 0.9}]
        prompt = persona.build_system_prompt(sources=sources, confidence_tier="ANSWER")
        assert "lint trap" in prompt

    def test_caveat_prompt_includes_disclaimer(self):
        persona = _make_persona()
        prompt = persona.build_system_prompt(sources=[], confidence_tier="CAVEAT")
        assert "verifying" in prompt.lower() or "recommend" in prompt.lower()

    def test_off_topic_message(self):
        persona = _make_persona()
        msg = persona.get_off_topic_message()
        assert "TestDryer" in msg

    def test_ambiguity_prompt(self):
        persona = _make_persona()
        msg = persona.build_ambiguity_prompt(["lint trap", "water filter"])
        assert "lint trap" in msg
        assert "water filter" in msg
