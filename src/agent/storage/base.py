from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from agent.protocol import Conversation, Document, Fragment, Kind, Message, ServerEvent


class Storage(ABC):
    """Persistent storage.

    This acts as a storage controller, providing high-level access to the various
    primitives. This also includes the publisher-subscriber system.

    """

    @abstractmethod
    async def get_document(self, id: str) -> Document:
        pass

    @abstractmethod
    async def get_document_by_key(self, key: str) -> Document:
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
    async def notify(self, kind: Kind, content: str) -> None:
        pass

    @abstractmethod
    async def create_document(self, key: str, title: str, tags: list[str], description: str, content: str) -> Document:
        pass

    @abstractmethod
    async def create_conversation(self, title: str) -> Conversation:
        pass

    @abstractmethod
    async def create_message(self, conversation_id: str, user_name: str) -> Message:
        pass

    @abstractmethod
    async def create_fragment(self, message_id: str, parent_id: str | None, kind: Kind, content: str) -> Fragment:
        pass

    @abstractmethod
    async def subscribe(self) -> AsyncIterator[ServerEvent]:
        pass
