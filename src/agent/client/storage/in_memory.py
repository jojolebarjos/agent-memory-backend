from typing import override

from agent.protocol import Conversation, Document, Fragment, Message

from .base import Storage


class InMemoryStorage(Storage):
    """..."""

    def __init__(self) -> None:
        self.documents = dict[str, Document]()
        self.conversations = dict[str, Conversation]()
        self.messages = dict[str, Message]()
        self.fragments = dict[str, Fragment]()

    @override
    async def get_document(self, id: str) -> Document:
        return self.documents[id]

    @override
    async def get_conversation(self, id: str) -> Conversation:
        return self.conversations[id]

    @override
    async def get_message(self, id: str) -> Message:
        return self.messages[id]

    @override
    async def get_fragment(self, id: str) -> Fragment:
        return self.fragments[id]

    @override
    async def add_document(self, document: Document) -> None:
        self.documents[document.id] = document
        # TODO embed document

    @override
    async def add_conversation(self, conversation: Conversation) -> None:
        self.conversations[conversation.id] = conversation

    @override
    async def add_message(self, message: Message) -> None:
        self.messages[message.id] = message

    @override
    async def add_fragment(self, fragment: Fragment) -> None:
        self.fragments[fragment.id] = fragment

    @override
    async def get_conversation_data(self, id: str) -> tuple[Conversation, list[Message], list[Fragment]]:
        conversation = self.conversations[id]
        messages = []
        fragments = []
        message_ids = set[str]()
        for message in self.messages.values():
            if message.conversation_id == id:
                messages.append(message)
                message_ids.add(message.id)
        for fragment in self.fragments.values():
            if fragment.message_id in message_ids:
                fragments.append(fragment)
        return conversation, messages, fragments

    # TODO query-based document search
