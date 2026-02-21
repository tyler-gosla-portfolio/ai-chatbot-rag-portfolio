import pytest


@pytest.mark.asyncio
async def test_create_chat_and_message(client, auth_headers):
    chat = await client.post("/api/v1/chats", json={"title": "Test Chat", "document_ids": []}, headers=auth_headers)
    assert chat.status_code == 201
    chat_id = chat.json()["id"]

    message = await client.post(
        f"/api/v1/chats/{chat_id}/messages",
        json={"content": "Summarize available context."},
        headers=auth_headers,
    )
    assert message.status_code == 201
    assert message.json()["role"] == "assistant"

    history = await client.get(f"/api/v1/chats/{chat_id}", headers=auth_headers)
    assert history.status_code == 200
    assert len(history.json()["messages"]) == 2
