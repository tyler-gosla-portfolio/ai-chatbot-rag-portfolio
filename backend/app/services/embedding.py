import hashlib
import math
from openai import AsyncOpenAI
from app.core.config import get_settings

settings = get_settings()


class EmbeddingService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def embed(self, text: str) -> list[float]:
        if self.client:
            response = await self.client.embeddings.create(model=settings.embedding_model, input=text)
            return response.data[0].embedding
        return self._local_embedding(text)

    def _local_embedding(self, text: str, dim: int = 64) -> list[float]:
        vec = [0.0] * dim
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = digest[0] % dim
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
