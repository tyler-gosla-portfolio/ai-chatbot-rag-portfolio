import pytest
import io
from httpx import AsyncClient

class TestDocumentFlow:
    @pytest.mark.asyncio
    async def test_upload_document(self, client: AsyncClient):
        # Register and login
        await client.post("/api/v1/auth/register", json={
            "email": "docuser@example.com",
            "password": "securepass123",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "docuser@example.com",
            "password": "securepass123",
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Upload a text file
        file_content = b"This is test document content for RAG processing. " * 20
        response = await client.post(
            "/api/v1/documents/",
            headers=headers,
            files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.txt"
        assert data["mime_type"] == "text/plain"
        assert data["status"] in ["ready", "pending", "processing"]

    @pytest.mark.asyncio
    async def test_list_documents(self, client: AsyncClient):
        # Register, login, upload
        await client.post("/api/v1/auth/register", json={
            "email": "listdoc@example.com",
            "password": "securepass123",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "listdoc@example.com",
            "password": "securepass123",
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Upload
        file_content = b"Test content for listing. " * 20
        await client.post(
            "/api/v1/documents/",
            headers=headers,
            files={"file": ("list_test.txt", io.BytesIO(file_content), "text/plain")},
        )

        # List
        response = await client.get("/api/v1/documents/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["documents"]) >= 1

    @pytest.mark.asyncio
    async def test_upload_unsupported_type(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "email": "badfile@example.com",
            "password": "securepass123",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "badfile@example.com",
            "password": "securepass123",
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/v1/documents/",
            headers=headers,
            files={"file": ("bad.exe", io.BytesIO(b"not allowed"), "application/octet-stream")},
        )
        assert response.status_code == 400
