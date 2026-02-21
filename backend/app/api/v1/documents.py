from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import User, Document, Chunk
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.services.documents import extract_text
from app.services.rag import RagService

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()
rag_service = RagService()


@router.post("", response_model=DocumentDetailResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in {"text/plain", "text/markdown", "application/pdf"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    raw = await file.read()
    upload_dir = Path(settings.uploads_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / f"{user.id}_{file.filename}"
    destination.write_bytes(raw)

    document = Document(
        user_id=user.id,
        filename=file.filename or "unknown",
        file_path=str(destination),
        file_size=len(raw),
        content_type=file.content_type or "application/octet-stream",
        status="processing",
    )
    db.add(document)
    await db.flush()

    text = extract_text(file.filename or "", raw)
    chunks = rag_service.chunk_text(text)
    chunk_rows: list[Chunk] = []
    total_tokens = 0

    for index, (content, token_count) in enumerate(chunks):
        embedding = await rag_service.embedding_service.embed(content)
        chunk_rows.append(
            Chunk(
                document_id=document.id,
                content=content,
                embedding=embedding,
                token_count=token_count,
                chunk_index=index,
                chunk_metadata={"filename": document.filename},
            )
        )
        total_tokens += token_count

    db.add_all(chunk_rows)
    document.status = "ready"
    document.chunk_count = len(chunk_rows)
    document.total_tokens = total_tokens

    await db.commit()
    await db.refresh(document)

    return DocumentDetailResponse(
        id=document.id,
        filename=document.filename,
        file_size=document.file_size,
        content_type=document.content_type,
        status=document.status,
        chunk_count=document.chunk_count,
        total_tokens=document.total_tokens,
        created_at=document.created_at,
        file_path=document.file_path,
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    docs = (await db.execute(select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc()))).scalars().all()
    return [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_size=d.file_size,
            content_type=d.content_type,
            status=d.status,
            chunk_count=d.chunk_count,
            total_tokens=d.total_tokens,
            created_at=d.created_at,
        )
        for d in docs
    ]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(document_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    document = await db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetailResponse(
        id=document.id,
        filename=document.filename,
        file_size=document.file_size,
        content_type=document.content_type,
        status=document.status,
        chunk_count=document.chunk_count,
        total_tokens=document.total_tokens,
        created_at=document.created_at,
        file_path=document.file_path,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    document = await db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    path = Path(document.file_path)
    if path.exists():
        path.unlink()

    await db.delete(document)
    await db.commit()
    return None
