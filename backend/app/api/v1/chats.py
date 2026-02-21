import time
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.security import decode_token
from app.db.session import get_db, SessionLocal
from app.models import User, Chat, ChatDocument, Message, Document, Chunk
from app.schemas.chat import CreateChatRequest, ChatResponse, ChatDetailResponse, MessageRequest, MessageResponse
from app.services.rag import RagService
from app.services.llm import LLMService

router = APIRouter(prefix="/chats", tags=["chats"])
rag_service = RagService()
llm_service = LLMService()


async def _get_chat_or_404(db: AsyncSession, chat_id: str, user_id: str) -> Chat:
    chat = await db.scalar(select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


async def _build_context(db: AsyncSession, chat: Chat, query: str, user_id: str):
    links = (await db.execute(select(ChatDocument).where(ChatDocument.chat_id == chat.id))).scalars().all()
    doc_ids = [l.document_id for l in links]

    if not doc_ids:
        user_docs = (await db.execute(select(Document.id).where(Document.user_id == user_id))).all()
        doc_ids = [row[0] for row in user_docs]

    if not doc_ids:
        return []

    chunks = (
        await db.execute(select(Chunk).where(Chunk.document_id.in_(doc_ids), Chunk.embedding.is_not(None)))
    ).scalars().all()

    q_embedding = await rag_service.query_embedding(query)
    scored = []
    for c in chunks:
        sim = rag_service.cosine_similarity(q_embedding, c.embedding or [])
        scored.append((sim, c))

    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:5]
    return [
        {
            "chunk_id": chunk.id,
            "content": chunk.content,
            "score": score,
            "document_id": chunk.document_id,
            "metadata": chunk.chunk_metadata or {},
        }
        for score, chunk in top
    ]


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(payload: CreateChatRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chat = Chat(user_id=user.id, title=payload.title or "New Chat")
    db.add(chat)
    await db.flush()

    if payload.document_ids:
        user_docs = (
            await db.execute(select(Document.id).where(Document.id.in_(payload.document_ids), Document.user_id == user.id))
        ).all()
        valid_doc_ids = {row[0] for row in user_docs}
        links = [ChatDocument(chat_id=chat.id, document_id=doc_id) for doc_id in payload.document_ids if doc_id in valid_doc_ids]
        db.add_all(links)

    await db.commit()
    await db.refresh(chat)
    return ChatResponse(id=chat.id, title=chat.title, created_at=chat.created_at, updated_at=chat.updated_at)


@router.get("", response_model=list[ChatResponse])
async def list_chats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chats = (await db.execute(select(Chat).where(Chat.user_id == user.id).order_by(Chat.updated_at.desc()))).scalars().all()
    return [ChatResponse(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at) for c in chats]


@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(chat_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chat = await _get_chat_or_404(db, chat_id, user.id)
    messages = (await db.execute(select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at.asc()))).scalars().all()
    links = (await db.execute(select(ChatDocument).where(ChatDocument.chat_id == chat.id))).scalars().all()

    return ChatDetailResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        document_ids=[l.document_id for l in links],
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                sources=m.sources,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(chat_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chat = await _get_chat_or_404(db, chat_id, user.id)
    await db.delete(chat)
    await db.commit()
    return None


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
async def list_messages(chat_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _get_chat_or_404(db, chat_id, user.id)
    messages = (await db.execute(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.asc()))).scalars().all()
    return [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            sources=m.sources,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    chat_id: str,
    payload: MessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat = await _get_chat_or_404(db, chat_id, user.id)

    user_message = Message(chat_id=chat.id, role="user", content=payload.content)
    db.add(user_message)
    await db.flush()

    started = time.perf_counter()
    context = await _build_context(db, chat, payload.content, user.id)
    prompt = rag_service.build_prompt(payload.content, context)
    answer = await llm_service.generate(prompt)
    latency = int((time.perf_counter() - started) * 1000)

    assistant_message = Message(
        chat_id=chat.id,
        role="assistant",
        content=answer,
        tokens_used=max(1, len(answer.split())),
        latency_ms=latency,
        sources=context,
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return MessageResponse(
        id=assistant_message.id,
        role=assistant_message.role,
        content=assistant_message.content,
        sources=assistant_message.sources,
        created_at=assistant_message.created_at,
    )


async def _authenticate_ws(websocket: WebSocket, db: AsyncSession) -> User | None:
    token = websocket.query_params.get("token")
    if not token:
        return None
    try:
        payload = decode_token(token)
    except Exception:
        return None

    if payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return await db.scalar(select(User).where(User.id == user_id))


@router.websocket("/{chat_id}/messages/stream")
async def stream_messages(websocket: WebSocket, chat_id: str):
    await websocket.accept()
    async with SessionLocal() as db:
        user = await _authenticate_ws(websocket, db)
        if not user:
            await websocket.send_json({"error": "unauthorized"})
            await websocket.close(code=1008)
            return

        chat = await db.scalar(select(Chat).where(Chat.id == chat_id, Chat.user_id == user.id))
        if not chat:
            await websocket.send_json({"error": "chat_not_found"})
            await websocket.close(code=1008)
            return

        try:
            while True:
                payload = await websocket.receive_json()
                content = payload.get("content", "").strip()
                if not content:
                    await websocket.send_json({"error": "empty_content"})
                    continue

                user_msg = Message(chat_id=chat.id, role="user", content=content)
                db.add(user_msg)
                await db.flush()

                context = await _build_context(db, chat, content, user.id)
                prompt = rag_service.build_prompt(content, context)
                assembled = []
                async for token in llm_service.stream_generate(prompt):
                    assembled.append(token)
                    await websocket.send_json({"delta": token})

                final_text = "".join(assembled).strip()
                assistant = Message(
                    chat_id=chat.id,
                    role="assistant",
                    content=final_text,
                    tokens_used=max(1, len(final_text.split())),
                    sources=context,
                )
                db.add(assistant)
                await db.commit()
                await websocket.send_json({"done": True, "sources": context})
        except WebSocketDisconnect:
            return
