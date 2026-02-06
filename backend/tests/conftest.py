"""Shared test fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_query():
    return "How do I clean the lint trap on my dryer?"


@pytest.fixture
def sample_chunks():
    return [
        {"text": "To clean the lint trap, open the door and pull the screen up.", "score": 0.92},
        {"text": "The lint trap should be cleaned after every load.", "score": 0.88},
        {"text": "Maintenance schedule recommends weekly deep cleaning.", "score": 0.75},
    ]
