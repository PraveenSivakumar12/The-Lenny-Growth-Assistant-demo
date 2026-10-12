"""
Tests for Health and System Diagnostics API
"""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "app" in data
    assert data["app"] == "The Lenny Growth Assistant"
    assert "database" in data
    assert "indexed_documents_count" in data
    assert data["indexed_documents_count"] > 0
