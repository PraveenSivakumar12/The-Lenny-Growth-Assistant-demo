"""
Tests for Artifact Creation, Retrieval, and Security Boundaries
"""

import pytest


@pytest.mark.asyncio
async def test_artifact_crud_and_persistence(client):
    # 1. Create a conversation
    c_res = await client.post("/api/conversations", json={"title": "Artifact Test Session"})
    conv_id = c_res.json()["id"]

    # 2. Post an artifact directly
    art_payload = {
        "conversation_id": conv_id,
        "title": "Interactive Retention Calculator",
        "artifact_type": "html",
        "content": "<!DOCTYPE html><html><body><h1>Calculator</h1></body></html>",
        "metadata_info": {"author": "assistant"}
    }
    create_art = await client.post("/api/artifacts", json=art_payload)
    assert create_art.status_code == 201
    artifact_id = create_art.json()["id"]

    # 3. Fetch single artifact
    get_art = await client.get(f"/api/artifacts/{artifact_id}")
    assert get_art.status_code == 200
    assert get_art.json()["title"] == "Interactive Retention Calculator"
    assert get_art.json()["artifact_type"] == "html"

    # 4. List artifacts filtered by conversation
    list_art = await client.get(f"/api/artifacts?conversation_id={conv_id}")
    assert list_art.status_code == 200
    assert len(list_art.json()) >= 1


@pytest.mark.asyncio
async def test_chat_triggers_artifact_generation(client):
    """Verifies that asking for an HTML component triggers artifact generation and persistence."""
    chat_res = await client.post("/api/chat", json={
        "message": "Create an interactive HTML UI component for a viral growth calculator",
        "provider": "mock"
    })
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert data["artifact"] is not None
    assert data["artifact"]["artifact_type"] == "html"
    assert "<html" in data["artifact"]["content"].lower() or "<div" in data["artifact"]["content"].lower()
