"""Ollama client mock for tests."""

from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def ollama_mock():
    """Mock Ollama client with predictable responses."""
    mock = Mock()
    mock.generate = AsyncMock(
        return_value={
            "response": "Mocked summary text",
            "done": True,
            "total_duration": 1_000_000_000,
        }
    )
    mock.embed = AsyncMock(
        return_value={
            "embedding": [0.1] * 512,
        }
    )
    mock.health = AsyncMock(return_value={"status": "ok"})
    return mock
