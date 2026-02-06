"""Document loader protocol and registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class LoadedDocument:
    text: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)
    source_uri: str = ""


@runtime_checkable
class DocumentLoader(Protocol):
    def load(self, source_uri: str) -> list[LoadedDocument]: ...

    @property
    def supported_extensions(self) -> list[str]: ...


_LOADER_REGISTRY: dict[str, type] = {}


def register_loader(source_type: str, loader_cls: type) -> None:
    _LOADER_REGISTRY[source_type] = loader_cls


def get_loader(source_type: str) -> DocumentLoader:
    if source_type not in _LOADER_REGISTRY:
        raise ValueError(f"No loader registered for source type: {source_type}")
    return _LOADER_REGISTRY[source_type]()


def _register_defaults():
    from app.ingestion.loaders.markdown_loader import MarkdownLoader
    from app.ingestion.loaders.pdf_loader import PDFLoader

    register_loader("markdown", MarkdownLoader)
    register_loader("pdf", PDFLoader)


_register_defaults()
