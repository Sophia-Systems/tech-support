"""LiteLLM-based LLM provider with streaming support."""

from __future__ import annotations

from typing import AsyncIterator

import litellm

from app.providers.base import LLMMessage, LLMResponse


class LiteLLMProvider:
    def __init__(
        self,
        model: str,
        api_key: str,
        api_base: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ):
        self._model = model
        self._api_key = api_key
        self._api_base = api_base
        self._temperature = temperature
        self._max_tokens = max_tokens

    def _to_messages(self, messages: list[LLMMessage]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        response = await litellm.acompletion(
            model=self._model,
            messages=self._to_messages(messages),
            api_key=self._api_key,
            api_base=self._api_base,
            temperature=temperature or self._temperature,
            max_tokens=max_tokens or self._max_tokens,
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            model=response.model or self._model,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        response = await litellm.acompletion(
            model=self._model,
            messages=self._to_messages(messages),
            api_key=self._api_key,
            api_base=self._api_base,
            temperature=temperature or self._temperature,
            max_tokens=max_tokens or self._max_tokens,
            stream=True,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
