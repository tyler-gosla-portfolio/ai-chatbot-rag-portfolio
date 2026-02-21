from openai import AsyncOpenAI
from app.core.config import get_settings

settings = get_settings()


class LLMService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def generate(self, prompt: str) -> str:
        if self.client:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return response.choices[0].message.content or ""
        return "Local fallback response: based on indexed content, this is the best available answer."

    async def stream_generate(self, prompt: str):
        if self.client:
            stream = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=0.2,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield delta
            return
        for token in "Local fallback streaming response.".split():
            yield token + " "
