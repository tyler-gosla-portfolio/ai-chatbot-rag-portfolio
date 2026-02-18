import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.chunk import Chunk
from app.schemas.document import DocumentResponse, DocumentListResponse, ChunkResponse
from app.api.deps import get_current_user
from app.config import settings
from app.services.document import process_document

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

def _doc_response(doc: Document) -> DocumentResponse:
    return DocumentResponse(
        id=str(doc.id),
        title=doc.title,
        filename=doc.filename,
        mime_type=doc.mime_type,
        file_size_bytes=doc.file_size_bytes,
        status=doc.status,
        error_message=doc.error_message,
        chunk_count=doc.chunk_count,
        created_at=doc.created_at.isoformat(),
        updated_at=doc.updated_at.isoformat(),
    )

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check document limit
    count_result = await db.execute(
        select(func.count()).select_from(Document).where(Document.user_id == current_user.id)
    )
    doc_count = count_result.scalar()
    if doc_count >= settings.MAX_DOCUMENTS_PER_USER:
        raise HTTPException(status_code=400, detail="Document limit reached")

    # Validate MIME type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

    # Read file
    content = await file.read()
    file_size = len(content)
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    # Save file locally
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename or "file")[1]
    local_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")
    with open(local_path, "wb") as f:
        f.write(content)

    # Create document record
    doc = Document(
        user_id=current_user.id,
        title=file.filename or "Untitled",
        filename=file.filename or "file",
        mime_type=content_type,
        file_size_bytes=file_size,
        s3_key=local_path,
        status="pending",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Process document in background (simplified: inline for now)
    try:
        await process_document(db, doc)
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        await db.commit()

    await db.refresh(doc)
    return _doc_response(doc)

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Document).where(Document.user_id == current_user.id)
    count_query = select(func.count()).select_from(Document).where(Document.user_id == current_user.id)

    if status_filter:
        query = query.where(Document.status == status_filter)
        count_query = count_query.where(Document.status == status_filter)

    query = query.order_by(Document.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    docs = result.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    return DocumentListResponse(
        documents=[_doc_response(d) for d in docs],
        total=total,
        page=page,
        page_size=page_size,
    )

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == uuid.UUID(doc_id), Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _doc_response(doc)

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == uuid.UUID(doc_id), Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    if os.path.exists(doc.s3_key):
        os.remove(doc.s3_key)

    await db.delete(doc)
    await db.commit()

@router.get("/{doc_id}/chunks", response_model=list[ChunkResponse])
async def list_chunks(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership
    doc_result = await db.execute(
        select(Document).where(Document.id == uuid.UUID(doc_id), Document.user_id == current_user.id)
    )
    if not doc_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")

    result = await db.execute(
        select(Chunk).where(Chunk.document_id == uuid.UUID(doc_id)).order_by(Chunk.chunk_index)
    )
    chunks = result.scalars().all()
    return [
        ChunkResponse(
            id=str(c.id),
            chunk_index=c.chunk_index,
            content=c.content,
            token_count=c.token_count,
            metadata=c.metadata_ or {},
        )
        for c in chunks
    ]
