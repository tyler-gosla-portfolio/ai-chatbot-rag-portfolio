import pytest
from httpx import AsyncClient
import io

class TestChatFlow:
    async def _setup_user(self, client: AsyncClient, email: str = "chatuser@example.com"):
        await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "securepass123",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "securepass123",
        })
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_create_conversation(self, client: AsyncClient):
        headers = await self._setup_user(client, "createconv@example.com")

        response = await client.post("/api/v1/conversations/", json={
            "title": "Test Chat",
        }, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Chat"

    @pytest.mark.asyncio
    async def test_list_conversations(self, client: AsyncClient):
        headers = await self._setup_user(client, "listconv@example.com")

        # Create a conversation
        await client.post("/api/v1/conversations/", json={
            "title": "My Chat",
        }, headers=headers)

        response = await client.get("/api/v1/conversations/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_send_message(self, client: AsyncClient):
        headers = await self._setup_user(client, "sendmsg@example.com")

        # Upload a document first
        file_content = b"Python is a programming language used for AI and web development. " * 20
        await client.post(
            "/api/v1/documents/",
            headers=headers,
            files={"file": ("python.txt", io.BytesIO(file_content), "text/plain")},
        )

        # Create conversation
        conv_resp = await client.post("/api/v1/conversations/", json={
            "title": "Python Chat",
        }, headers=headers)
        convo_id = conv_resp.json()["id"]

        # Send message
        response = await client.post(
            f"/api/v1/conversations/{convo_id}/messages/",
            json={"content": "What is Python?"},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "assistant"
        assert len(data["content"]) > 0

    @pytest.mark.asyncio
    async def test_list_messages(self, client: AsyncClient):
        headers = await self._setup_user(client, "listmsg@example.com")

        # Create conversation and send message
        conv_resp = await client.post("/api/v1/conversations/", json={
            "title": "Msg List Chat",
        }, headers=headers)
        convo_id = conv_resp.json()["id"]

        await client.post(
            f"/api/v1/conversations/{convo_id}/messages/",
            json={"content": "Hello!"},
            headers=headers,
        )

        # List messages
        response = await client.get(
            f"/api/v1/conversations/{convo_id}/messages/",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) >= 2  # user + assistant

    @pytest.mark.asyncio
    async def test_message_feedback(self, client: AsyncClient):
        headers = await self._setup_user(client, "feedback@example.com")

        conv_resp = await client.post("/api/v1/conversations/", json={
            "title": "Feedback Chat",
        }, headers=headers)
        convo_id = conv_resp.json()["id"]

        msg_resp = await client.post(
            f"/api/v1/conversations/{convo_id}/messages/",
            json={"content": "Test feedback"},
            headers=headers,
        )
        msg_id = msg_resp.json()["id"]

        # Submit feedback
        response = await client.post(
            f"/api/v1/conversations/{convo_id}/messages/{msg_id}/feedback",
            json={"feedback": 1},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["feedback"] == 1
