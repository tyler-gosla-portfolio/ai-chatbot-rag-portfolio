from fastapi.testclient import TestClient
from app.main import create_app


def test_websocket_rejects_without_auth():
    app = create_app()
    with TestClient(app) as client:
        with client.websocket_connect("/api/v1/chats/fake/messages/stream") as ws:
            message = ws.receive_json()
            assert message["error"] in {"unauthorized", "chat_not_found"}
