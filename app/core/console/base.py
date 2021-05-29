from abc import ABC, abstractmethod
from typing import Any, AsyncIterable, Callable, Awaitable, Union
import uuid


class BaseCommandExecution(ABC):
    @abstractmethod
    async def execute(self, command: str) -> None:
        ...

    @abstractmethod
    async def output(self) -> AsyncIterable[str]:
        ...


AsyncStrCallback = Callable[[str], Awaitable[None]]


class BaseCommandExecutor(ABC):
    @abstractmethod
    async def execute(self, command: Union[list[str], str]) -> uuid.UUID:
        ...

    @abstractmethod
    def finished(self, execution_id: uuid.UUID) -> bool:
        ...

    @abstractmethod
    def result(self, execution_id: uuid.UUID) -> str:
        ...

    @abstractmethod
    def __contains__(self, execution_id: Union[uuid.UUID, Any]) -> bool:
        ...

    @abstractmethod
    async def listen(self, callback: AsyncStrCallback, execution_id: uuid.UUID) -> None:
        ...