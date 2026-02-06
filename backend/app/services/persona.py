"""Persona service — system prompt assembly via Jinja2 templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Template

from app.core.config import PersonaConfig

_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


class PersonaService:
    def __init__(self, config: PersonaConfig):
        self.config = config
        self._template_data = self._load_template()

    def _load_template(self) -> dict[str, Any]:
        path = _CONFIG_DIR / self.config.template_path
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def build_system_prompt(
        self,
        sources: list[dict[str, Any]],
        confidence_tier: str = "ANSWER",
    ) -> str:
        template_str = self._template_data.get("system_prompt", "You are a helpful assistant.")
        template = Template(template_str)
        return template.render(
            company_name=self.config.company_name,
            product_name=self.config.product_name,
            tone=self.config.tone,
            sources=sources,
            confidence_tier=confidence_tier,
        )

    def get_fallback_message(self) -> str:
        template_str = self._template_data.get(
            "fallback_message", "I couldn't find specific information about that."
        )
        return Template(template_str).render(
            product_name=self.config.product_name,
        )

    def get_escalation_message(self) -> str:
        template_str = self._template_data.get(
            "escalation_message", "Let me connect you with a human agent."
        )
        return Template(template_str).render(
            product_name=self.config.product_name,
        )

    def get_off_topic_message(self) -> str:
        template_str = self._template_data.get(
            "off_topic_message",
            f"I can only help with questions about {self.config.product_name}.",
        )
        return Template(template_str).render(
            product_name=self.config.product_name,
        )

    def build_ambiguity_prompt(self, topics: list[str]) -> str:
        topic_list = " and ".join(f"'{t}'" for t in topics[:3])
        return f"I found information about {topic_list} — could you clarify which one you're asking about?"
