"""Ollama API mock fixture."""
import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def ollama_mock():
    """Mock Ollama client that returns predictable responses."""
    mock = Mock()
    mock.generate = AsyncMock(return_value={
        "response": "Mocked Ollama response",
        "done": True,
        "total_duration": 1234567890,
    })
    mock.embed = AsyncMock(return_value={
        "embedding": [0.1] * 4096,
    })
    mock.health = AsyncMock(return_value={"status": "ok"})
    return mock
