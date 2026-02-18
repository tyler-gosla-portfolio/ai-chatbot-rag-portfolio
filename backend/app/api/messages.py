import uuid
import time
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.message import (
    SendMessageRequest, FeedbackRequest,
    MessageResponse, MessageListResponse, SourceInfo,
)
from app.api.deps import get_current_user
from app.services.chat import generate_response

router = APIRouter()

def _msg_response(msg: Message) -> MessageResponse:
    sources = []
    if msg.sources:
        for s in msg.sources:
            sources.append(SourceInfo(
                document_id=s.get("document_id", ""),
                chunk_index=s.get("chunk_index", 0),
                content_preview=s.get("content_preview", ""),
                similarity=s.get("similarity", 0.0),
            ))
    return MessageResponse(
        id=str(msg.id),
        conversation_id=str(msg.conversation_id),
        role=msg.role,
        content=msg.content,
        token_count=msg.token_count,
        latency_ms=msg.latency_ms,
        model=msg.model,
        sources=sources,
        feedback=msg.feedback,
        created_at=msg.created_at.isoformat(),
    )

async def _get_conversation(convo_id: str, user: User, db: AsyncSession) -> Conversation:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == uuid.UUID(convo_id),
            Conversation.user_id == user.id,
        )
    )
    convo = result.scalar_one_or_none()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: str,
    req: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    convo = await _get_conversation(conversation_id, current_user, db)

    # Save user message
    user_msg = Message(
        conversation_id=convo.id,
        role="user",
        content=req.content,
    )
    db.add(user_msg)
    await db.commit()

    # Generate AI response
    start = time.time()
    response_content, sources = await generate_response(db, convo, req.content)
    latency_ms = int((time.time() - start) * 1000)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=convo.id,
        role="assistant",
        content=response_content,
        model="gpt-4o",
        latency_ms=latency_ms,
        sources=sources,
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    return _msg_response(assistant_msg)

@router.get("/", response_model=MessageListResponse)
async def list_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    before: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_conversation(conversation_id, current_user, db)

    query = select(Message).where(
        Message.conversation_id == uuid.UUID(conversation_id)
    )

    if before:
        # Cursor-based pagination
        cursor_msg = await db.execute(
            select(Message).where(Message.id == uuid.UUID(before))
        )
        cursor = cursor_msg.scalar_one_or_none()
        if cursor:
            query = query.where(Message.created_at < cursor.created_at)

    query = query.order_by(Message.created_at.desc()).limit(limit + 1)
    result = await db.execute(query)
    messages = list(result.scalars().all())

    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]

    # Return in chronological order
    messages.reverse()

    return MessageListResponse(
        messages=[_msg_response(m) for m in messages],
        has_more=has_more,
    )

@router.post("/{msg_id}/feedback", response_model=MessageResponse)
async def submit_feedback(
    conversation_id: str,
    msg_id: str,
    req: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_conversation(conversation_id, current_user, db)

    result = await db.execute(
        select(Message).where(
            Message.id == uuid.UUID(msg_id),
            Message.conversation_id == uuid.UUID(conversation_id),
        )
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    msg.feedback = req.feedback
    await db.commit()
    await db.refresh(msg)
    return _msg_response(msg)
