"""Path validation to prevent directory traversal attacks."""

from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import CSBotError


class PathTraversalError(CSBotError):
    """Raised when a file path escapes the allowed base directory."""


def validate_file_path(source_uri: str) -> Path:
    """Resolve a file path and verify it's within the allowed base directory.

    Returns the resolved Path.
    Raises PathTraversalError if the path escapes the allowed directory.
    """
    path = Path(source_uri).resolve()

    allowed_base = get_settings().ingestion.allowed_base_dir
    if allowed_base:
        base = Path(allowed_base).resolve()
        if not path.is_relative_to(base):
            raise PathTraversalError(
                f"Path {path} is outside allowed base directory {base}"
            )

    return path
