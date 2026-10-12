"""
Tests for Conversations Lifecycle and Session Isolation
"""

import pytest


@pytest.mark.asyncio
async def test_conversation_lifecycle(client):
    # 1. Create conversation
    create_res = await client.post("/api/conversations", json={"title": "Product Strategy Q&A"})
    assert create_res.status_code == 201
    conv = create_res.json()
    conv_id = conv["id"]
    assert conv["title"] == "Product Strategy Q&A"

    # 2. List conversations
    list_res = await client.get("/api/conversations")
    assert list_res.status_code == 200
    convs = list_res.json()
    assert any(c["id"] == conv_id for c in convs)

    # 3. Rename conversation
    rename_res = await client.patch(f"/api/conversations/{conv_id}", json={"title": "B2B Growth Loops"})
    assert rename_res.status_code == 200
    assert rename_res.json()["title"] == "B2B Growth Loops"

    # 4. Fetch detail
    detail_res = await client.get(f"/api/conversations/{conv_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == "B2B Growth Loops"
    assert len(detail["messages"]) == 0

    # 5. Delete conversation
    del_res = await client.delete(f"/api/conversations/{conv_id}")
    assert del_res.status_code == 204

    # 6. Verify 404
    get_res = await client.get(f"/api/conversations/{conv_id}")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_session_isolation(client):
    """Verifies that messages sent to Conversation A do not appear in Conversation B."""
    # Create Conv A
    res_a = await client.post("/api/conversations", json={"title": "Session A"})
    id_a = res_a.json()["id"]

    # Create Conv B
    res_b = await client.post("/api/conversations", json={"title": "Session B"})
    id_b = res_b.json()["id"]

    # Send message to A
    await client.post("/api/chat", json={
        "conversation_id": id_a,
        "message": "What is the aha moment according to Elena Verna?",
        "provider": "mock"
    })

    # Send message to B
    await client.post("/api/chat", json={
        "conversation_id": id_b,
        "message": "Tell me about pricing models.",
        "provider": "mock"
    })

    # Retrieve A
    detail_a = (await client.get(f"/api/conversations/{id_a}")).json()
    detail_b = (await client.get(f"/api/conversations/{id_b}")).json()

    # Verify message isolation
    contents_a = [m["content"] for m in detail_a["messages"]]
    contents_b = [m["content"] for m in detail_b["messages"]]

    query_a = "What is the aha moment according to Elena Verna?"
    query_b = "Tell me about pricing models."
    assert query_a in contents_a
    assert query_b not in contents_a
    assert query_b in contents_b
    assert query_a not in contents_b
