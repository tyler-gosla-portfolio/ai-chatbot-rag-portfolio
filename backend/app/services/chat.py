from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from app.services.rag import retrieve_relevant_chunks, build_rag_prompt
from app.config import settings

async def generate_response(
    db: AsyncSession,
    conversation: Conversation,
    user_message: str,
) -> tuple[str, list[dict]]:
    """Generate an AI response for a user message using RAG."""
    # Retrieve relevant chunks
    sources = await retrieve_relevant_chunks(db, user_message, conversation)

    # Build prompt
    messages = build_rag_prompt(
        user_message,
        sources,
        system_prompt=conversation.system_prompt,
    )

    # Generate response
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        if settings.OPENAI_API_KEY.startswith("sk-test"):
            # Mock response for testing
            source_refs = ""
            if sources:
                refs = [f"[{s['document_title']}:chunk_{s['chunk_index']}]" for s in sources[:3]]
                source_refs = f"\n\nSources: {', '.join(refs)}"
            return (
                f"Based on the provided context, here is my response to your query: '{user_message}'. "
                f"I found {len(sources)} relevant chunks from your documents.{source_refs}",
                [
                    {
                        "document_id": s["document_id"],
                        "chunk_index": s["chunk_index"],
                        "content_preview": s["content_preview"],
                        "similarity": s["similarity"],
                    }
                    for s in sources
                ],
            )

        response = await client.chat.completions.create(
            model=settings.COMPLETION_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )

        content = response.choices[0].message.content or ""
        source_info = [
            {
                "document_id": s["document_id"],
                "chunk_index": s["chunk_index"],
                "content_preview": s["content_preview"],
                "similarity": s["similarity"],
            }
            for s in sources
        ]

        return content, source_info

    except Exception as e:
        return f"I encountered an error generating a response: {str(e)}", []
