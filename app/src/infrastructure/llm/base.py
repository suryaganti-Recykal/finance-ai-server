from abc import ABC, abstractmethod
from typing import TypedDict


class ChatMessage(TypedDict):
    role: str
    content: str


class LLMClient(ABC):
    """Port for a chat-completion LLM provider.

    Agents (finance copilot, monthly report insights, anomaly explanations)
    depend on this interface rather than a specific vendor SDK, so the
    provider can be swapped or A/B tested per agent without touching
    agent logic.
    """

    @abstractmethod
    async def chat(
        self, messages: list[ChatMessage], *, temperature: float = 0.2, max_tokens: int = 1024
    ) -> str: ...
