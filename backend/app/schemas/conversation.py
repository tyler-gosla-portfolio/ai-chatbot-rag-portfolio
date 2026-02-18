from pydantic import BaseModel, Field

class CreateConversationRequest(BaseModel):
    title: str | None = None
    document_ids: list[str] = []
    system_prompt: str | None = None

class UpdateConversationRequest(BaseModel):
    title: str | None = None
    system_prompt: str | None = None
    document_ids: list[str] | None = None

class ConversationResponse(BaseModel):
    id: str
    title: str | None
    model: str
    system_prompt: str | None
    created_at: str
    updated_at: str
    document_ids: list[str] = []

    model_config = {"from_attributes": True}

class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
