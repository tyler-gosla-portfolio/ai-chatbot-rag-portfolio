import io
import pytest


@pytest.mark.asyncio
async def test_upload_list_get_delete_document(client, auth_headers):
    content = io.BytesIO(b"This is a simple document for RAG testing.")
    files = {"file": ("sample.txt", content, "text/plain")}

    uploaded = await client.post("/api/v1/documents", files=files, headers=auth_headers)
    assert uploaded.status_code == 201
    document_id = uploaded.json()["id"]

    listed = await client.get("/api/v1/documents", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    detail = await client.get(f"/api/v1/documents/{document_id}", headers=auth_headers)
    assert detail.status_code == 200

    deleted = await client.delete(f"/api/v1/documents/{document_id}", headers=auth_headers)
    assert deleted.status_code == 204
