from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    content_type: str
    status: str
    chunk_count: int
    total_tokens: int
    created_at: datetime


class DocumentDetailResponse(DocumentResponse):
    file_path: str
