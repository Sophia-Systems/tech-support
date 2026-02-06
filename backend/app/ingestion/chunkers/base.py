"""Chunking strategy protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class Chunk:
    text: str
    index: int
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


@runtime_checkable
class ChunkingStrategy(Protocol):
    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]: ...
