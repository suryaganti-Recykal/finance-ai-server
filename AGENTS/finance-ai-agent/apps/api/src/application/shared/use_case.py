from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class UseCase(ABC, Generic[InputT, OutputT]):
    """Base for a single application-layer use case (one class per business action).

    Routers depend on use cases, never on repositories or ORM models directly -
    this keeps the API layer a thin adapter over the application layer.
    """

    @abstractmethod
    async def execute(self, input_data: InputT) -> OutputT: ...
