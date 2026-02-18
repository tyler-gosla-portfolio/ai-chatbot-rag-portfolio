import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.conversation import (
    CreateConversationRequest, UpdateConversationRequest,
    ConversationResponse, ConversationListResponse,
)
from app.api.deps import get_current_user

router = APIRouter()

def _convo_response(convo: Conversation) -> ConversationResponse:
    return ConversationResponse(
        id=str(convo.id),
        title=convo.title,
        model=convo.model,
        system_prompt=convo.system_prompt,
        created_at=convo.created_at.isoformat(),
        updated_at=convo.updated_at.isoformat(),
    )

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    req: CreateConversationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    convo = Conversation(
        user_id=current_user.id,
        title=req.title or "New Conversation",
        system_prompt=req.system_prompt,
    )
    db.add(convo)
    await db.commit()
    await db.refresh(convo)
    return _convo_response(convo)

@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    convos = result.scalars().all()
    return ConversationListResponse(
        conversations=[_convo_response(c) for c in convos],
        total=len(convos),
    )

@router.get("/{convo_id}", response_model=ConversationResponse)
async def get_conversation(
    convo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == uuid.UUID(convo_id),
            Conversation.user_id == current_user.id,
        )
    )
    convo = result.scalar_one_or_none()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _convo_response(convo)

@router.patch("/{convo_id}", response_model=ConversationResponse)
async def update_conversation(
    convo_id: str,
    req: UpdateConversationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == uuid.UUID(convo_id),
            Conversation.user_id == current_user.id,
        )
    )
    convo = result.scalar_one_or_none()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if req.title is not None:
        convo.title = req.title
    if req.system_prompt is not None:
        convo.system_prompt = req.system_prompt

    await db.commit()
    await db.refresh(convo)
    return _convo_response(convo)

@router.delete("/{convo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    convo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == uuid.UUID(convo_id),
            Conversation.user_id == current_user.id,
        )
    )
    convo = result.scalar_one_or_none()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(convo)
    await db.commit()
