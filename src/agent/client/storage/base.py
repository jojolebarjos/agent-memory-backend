from abc import ABC, abstractmethod

from agent.protocol import Conversation, Document, Fragment, Message


class Storage(ABC):
    """..."""

    @abstractmethod
    async def get_document(self, id: str) -> Document:
        pass

    @abstractmethod
    async def get_conversation(self, id: str) -> Conversation:
        pass

    @abstractmethod
    async def get_message(self, id: str) -> Message:
        pass

    @abstractmethod
    async def get_fragment(self, id: str) -> Fragment:
        pass

    @abstractmethod
    async def add_document(self, document: Document) -> None:
        pass

    @abstractmethod
    async def add_conversation(self, conversation: Conversation) -> None:
        pass

    @abstractmethod
    async def add_message(self, message: Message) -> None:
        pass

    @abstractmethod
    async def add_fragment(self, fragment: Fragment) -> None:
        pass

    @abstractmethod
    async def get_conversation_data(self, id: str) -> tuple[Conversation, list[Message], list[Fragment]]:
        pass

    # TODO query-based document search
