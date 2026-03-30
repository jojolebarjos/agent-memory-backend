from abc import ABC, abstractmethod

from agent.context import Context


class Agent(ABC):
    """Conversational agent.

    An agent are stateless handlers that generate a single message (possibly made of
    many fragments), given the current context (i.e., conversation history and available
    documents).

    """

    @abstractmethod
    async def reply_to(self, context: Context) -> None:
        pass
