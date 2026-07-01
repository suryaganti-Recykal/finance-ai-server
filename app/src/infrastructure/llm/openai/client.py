from openai import AsyncOpenAI

from src.core.config.settings import get_settings
from src.infrastructure.llm.base import ChatMessage, LLMClient


class OpenAILLMClient(LLMClient):
    def __init__(self, model: str = "gpt-4o") -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = model

    async def chat(
        self, messages: list[ChatMessage], *, temperature: float = 0.2, max_tokens: int = 1024
    ) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
