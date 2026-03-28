import asyncio
from collections.abc import AsyncIterator

from pydantic import BaseModel

from agent.agent import Agent
from agent.utility import make_id, make_timestamp

from .protocol import (
    ClientCommand,
    Conversation,
    ConversationCreateCommand,
    ConversationCreatedEvent,
    Document,
    DocumentCreatedEvent,
    Fragment,
    FragmentCreatedEvent,
    FragmentKind,
    Message,
    MessageCreateCommand,
    MessageCreatedEvent,
    ServerEvent,
    WorkspaceSyncEvent,
)


class Role(BaseModel):
    user_id: str


class Controller:
    """..."""

    def __init__(self, agent: Agent) -> None:
        self.agent = agent
        # TODO these objects should be per-workspace
        self.events = list[ServerEvent]()
        self.documents = dict[str, Document]()
        self.document_by_key = dict[str, dict[int, Document]]()
        self.conversations = dict[str, Conversation]()
        self.messages = dict[str, Message]()
        self.fragments = dict[str, Fragment]()

    async def create_document(self, key: str, title: str, tags: list[str], description: str, content: str) -> Document:
        """..."""

        if key not in self.document_by_key:
            self.document_by_key[key] = {}
            version = 1
        else:
            version = max(self.document_by_key[key].keys()) + 1

        document = Document(
            id=make_id(),
            created_at=make_timestamp(),
            key=key,
            version=version,
            title=title,
            tags=tags,
            description=description,
            content=content,
        )

        assert document.id not in self.documents
        self.documents[document.id] = document
        self.document_by_key[key][version] = document

        event = DocumentCreatedEvent(document=document)
        await self.publish(event)

        return document

    async def create_conversation(self, title: str) -> Conversation:
        """..."""

        conversation = Conversation(
            id=make_id(),
            created_at=make_timestamp(),
            title=title,
        )

        assert conversation.id not in self.conversations
        self.conversations[conversation.id] = conversation

        event = ConversationCreatedEvent(conversation=conversation)
        await self.publish(event)

        return conversation

    async def create_message(self, conversation_id: str, user_name: str) -> Message:
        """..."""

        if conversation_id not in self.conversations:
            raise KeyError(conversation_id)

        message = Message(
            id=make_id(),
            created_at=make_timestamp(),
            conversation_id=conversation_id,
            user_name=user_name,
        )

        assert message.id not in self.messages
        self.messages[message.id] = message

        event = MessageCreatedEvent(message=message)
        await self.publish(event)

        return message

    async def create_fragment(
        self,
        message_id: str,
        parent_id: str | None,
        kind: FragmentKind,
        content: str,
    ) -> Fragment:
        """..."""

        if message_id not in self.messages:
            raise KeyError(message_id)

        fragment = Fragment(
            id=make_id(),
            created_at=make_timestamp(),
            message_id=message_id,
            parent_id=parent_id,
            kind=kind,
            content=content,
        )

        assert fragment.id not in self.fragments
        self.fragments[fragment.id] = fragment

        event = FragmentCreatedEvent(fragment=fragment)
        await self.publish(event)

        return fragment

    async def execute(self, role: Role, command: ClientCommand) -> None:
        """..."""

        match command:
            case ConversationCreateCommand(title=title):
                _ = await self.create_conversation(title)
            case MessageCreateCommand(conversation_id=conversation_id, content=content):
                user_name = role.user_id  # TODO get actual user name
                message = await self.create_message(conversation_id, user_name)
                _ = await self.create_fragment(message.id, None, FragmentKind.TEXT, content)
            case _:
                raise ValueError

    async def publish(self, event: ServerEvent) -> None:
        """..."""

        # TODO proper synchronization primitive
        self.events.append(event)

    async def subscribe(self, role: Role, last_event_id: str | None = None) -> AsyncIterator[ServerEvent]:
        """..."""

        # Restore history
        offset = 0
        count = len(self.events)
        yield WorkspaceSyncEvent(count=count)
        while offset < count:
            yield self.events[offset]
            offset += 1

        # Continue streaming new messages indefinitely
        while True:
            if offset < len(self.events):
                yield self.events[offset]
                offset += 1
                continue

            # Wait for new events
            # TODO use clean synchronization primitive
            await asyncio.sleep(0.1)
