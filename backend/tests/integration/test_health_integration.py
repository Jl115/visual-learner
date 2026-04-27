"""Integration smoke test for the full application stack."""

from __future__ import annotations

import pytest
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_health_integration(client: TestClient) -> None:
    """Smoke test: assert the application boots and the health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
