from abc import ABC, abstractmethod

from .context import Context


class Agent(ABC):
    """..."""

    @abstractmethod
    async def reply_to(self, context: Context) -> None:
        pass
