"""Domain exceptions."""

from __future__ import annotations


class CSBotError(Exception):
    """Base exception for the application."""


class DocumentNotFoundError(CSBotError):
    def __init__(self, document_id: str):
        super().__init__(f"Document not found: {document_id}")
        self.document_id = document_id


class SessionNotFoundError(CSBotError):
    def __init__(self, session_id: str):
        super().__init__(f"Session not found: {session_id}")
        self.session_id = session_id


class IngestionError(CSBotError):
    """Raised when document ingestion fails."""


class ProviderError(CSBotError):
    """Raised when a provider call fails."""


class EscalationError(CSBotError):
    """Raised when escalation dispatch fails."""


class ConfigurationError(CSBotError):
    """Raised for invalid configuration."""
