from anthropic import AsyncAnthropic

from src.core.config.settings import get_settings
from src.infrastructure.llm.base import ChatMessage, LLMClient


class ClaudeLLMClient(LLMClient):
    def __init__(self, model: str = "claude-sonnet-4-6") -> None:
        settings = get_settings()
        self._client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._model = model

    async def chat(
        self, messages: list[ChatMessage], *, temperature: float = 0.2, max_tokens: int = 1024
    ) -> str:
        system = next((m["content"] for m in messages if m["role"] == "system"), None)
        conversation = [m for m in messages if m["role"] != "system"]
        response = await self._client.messages.create(
            model=self._model,
            system=system,
            messages=conversation,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return "".join(block.text for block in response.content if block.type == "text")
