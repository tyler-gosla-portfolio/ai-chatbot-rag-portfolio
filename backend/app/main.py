from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, conversations, documents, health, messages
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="AI Chatbot RAG API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
    app.include_router(
        conversations.router, prefix="/api/v1/conversations", tags=["conversations"]
    )
    app.include_router(
        messages.router,
        prefix="/api/v1/conversations/{conversation_id}/messages",
        tags=["messages"],
    )
    app.include_router(health.router, tags=["health"])

    return app


app = create_app()
