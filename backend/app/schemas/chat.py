from datetime import datetime
from pydantic import BaseModel, Field


class CreateChatRequest(BaseModel):
    title: str | None = None
    document_ids: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    id: str
    title: str | None
    created_at: datetime
    updated_at: datetime


class MessageRequest(BaseModel):
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: list[dict] | None = None
    created_at: datetime


class ChatDetailResponse(ChatResponse):
    messages: list[MessageResponse]
    document_ids: list[str]
