from pydantic import BaseModel, Field

class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)

class FeedbackRequest(BaseModel):
    feedback: int = Field(..., ge=-1, le=1)

class SourceInfo(BaseModel):
    document_id: str
    chunk_index: int
    content_preview: str
    similarity: float

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    token_count: int | None = None
    latency_ms: int | None = None
    model: str | None = None
    sources: list[SourceInfo] = []
    feedback: int | None = None
    created_at: str

    model_config = {"from_attributes": True}

class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    has_more: bool
