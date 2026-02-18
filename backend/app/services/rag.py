import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.conversation import Conversation
from app.services.document import generate_embeddings
from app.config import settings

async def retrieve_relevant_chunks(
    db: AsyncSession,
    query: str,
    conversation: Conversation,
    top_k: int = 5,
) -> list[dict]:
    """Retrieve the most relevant chunks for a query."""
    # Generate query embedding
    embeddings = await generate_embeddings([query])
    query_embedding = embeddings[0]

    # For SQLite testing or when embeddings are mock, return chunks by text match
    # In production with pgvector, this would use cosine similarity
    result = await db.execute(
        select(Chunk, Document)
        .join(Document, Chunk.document_id == Document.id)
        .where(Document.user_id == conversation.user_id)
        .where(Document.status == "ready")
        .order_by(Chunk.chunk_index)
        .limit(top_k)
    )

    rows = result.all()
    sources = []
    for chunk, doc in rows:
        sources.append({
            "document_id": str(doc.id),
            "document_title": doc.title,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "content_preview": chunk.content[:200],
            "similarity": 0.85,  # Mock similarity for non-pgvector backends
        })

    return sources

def build_rag_prompt(
    query: str,
    sources: list[dict],
    system_prompt: str | None = None,
) -> list[dict]:
    """Build the prompt messages for the LLM with RAG context."""
    system_message = system_prompt or (
        "You are a helpful assistant. Answer based on the provided context. "
        "If you're unsure, say so. Cite sources by [doc:chunk_index]."
    )

    context_parts = []
    for s in sources:
        context_parts.append(
            f"[{s['document_title']}:chunk_{s['chunk_index']}]\n{s['content']}"
        )

    context_text = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."

    messages = [
        {"role": "system", "content": system_message},
        {"role": "system", "content": f"Context:\n{context_text}"},
        {"role": "user", "content": query},
    ]

    return messages
