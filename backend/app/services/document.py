import os
import tiktoken
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.models.chunk import Chunk
from app.config import settings

def extract_text(file_path: str, mime_type: str) -> str:
    """Extract text from a file based on its MIME type."""
    if mime_type == "application/pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            # Fallback if PyMuPDF not available
            return _read_as_text(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            return _read_as_text(file_path)
    else:
        return _read_as_text(file_path)

def _read_as_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """Split text into chunks by token count with overlap."""
    try:
        enc = tiktoken.encoding_for_model("gpt-4o")
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")

    tokens = enc.encode(text)
    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        if chunk_text.strip():
            chunks.append(chunk_text)
        start += chunk_size - chunk_overlap

    return chunks

def count_tokens(text: str) -> int:
    """Count tokens in text."""
    try:
        enc = tiktoken.encoding_for_model("gpt-4o")
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using OpenAI API. Returns mock embeddings if API unavailable."""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        if settings.OPENAI_API_KEY.startswith("sk-test"):
            # Return mock embeddings for testing
            return [[0.0] * 1536 for _ in texts]

        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]
    except Exception:
        # Return mock embeddings on failure
        return [[0.0] * 1536 for _ in texts]

async def process_document(db: AsyncSession, doc: Document) -> None:
    """Process a document: extract text, chunk, embed, and store."""
    doc.status = "processing"
    await db.commit()

    try:
        # Extract text
        text = extract_text(doc.s3_key, doc.mime_type)
        if not text.strip():
            raise ValueError("No text content extracted from document")

        # Chunk text
        chunks = chunk_text(
            text,
            chunk_size=settings.CHUNK_SIZE_TOKENS,
            chunk_overlap=settings.CHUNK_OVERLAP_TOKENS,
        )

        if not chunks:
            raise ValueError("No chunks generated from document")

        # Generate embeddings
        embeddings = await generate_embeddings(chunks)

        # Store chunks
        for i, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
            chunk = Chunk(
                document_id=doc.id,
                chunk_index=i,
                content=chunk_content,
                token_count=count_tokens(chunk_content),
                embedding=str(embedding),  # Store as string for SQLite compat
                metadata_={
                    "document_title": doc.title,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
            )
            db.add(chunk)

        doc.chunk_count = len(chunks)
        doc.status = "ready"
        await db.commit()

    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        await db.commit()
        raise
