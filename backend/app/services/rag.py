import math
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import get_settings
from app.services.embedding import EmbeddingService

settings = get_settings()


class RagService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()

    def chunk_text(self, text: str) -> list[tuple[str, int]]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size * 4,
            chunk_overlap=settings.chunk_overlap * 4,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )
        chunks = splitter.split_text(text)
        return [(chunk, max(1, len(chunk.split()))) for chunk in chunks if chunk.strip()]

    async def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        return [await self.embedding_service.embed(chunk) for chunk in chunks]

    async def query_embedding(self, query: str) -> list[float]:
        return await self.embedding_service.embed(query)

    @staticmethod
    def cosine_similarity(v1: list[float], v2: list[float]) -> float:
        if not v1 or not v2:
            return 0.0
        length = min(len(v1), len(v2))
        dot = sum(v1[i] * v2[i] for i in range(length))
        n1 = math.sqrt(sum(v * v for v in v1[:length])) or 1.0
        n2 = math.sqrt(sum(v * v for v in v2[:length])) or 1.0
        return dot / (n1 * n2)

    def build_prompt(self, query: str, contexts: list[dict]) -> str:
        joined = "\n\n".join(f"[{i + 1}] {c['content']}" for i, c in enumerate(contexts))
        return (
            "You are a helpful assistant answering questions using the provided context. "
            "If context is insufficient, say so clearly.\n\n"
            f"Context:\n{joined}\n\n"
            f"Question: {query}\n"
            "Answer concisely and cite source numbers like [1], [2]."
        )
