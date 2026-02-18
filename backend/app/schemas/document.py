from pydantic import BaseModel, Field

class DocumentResponse(BaseModel):
    id: str
    title: str
    filename: str
    mime_type: str
    file_size_bytes: int
    status: str
    error_message: str | None = None
    chunk_count: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int

class ChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    token_count: int
    metadata: dict = {}

    model_config = {"from_attributes": True}
