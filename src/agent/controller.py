from collections.abc import AsyncIterator

from pydantic import BaseModel

from agent.agent import Agent
from agent.context import Context
from agent.storage import Storage

from .protocol import (
    ClientCommand,
    ConversationCreateCommand,
    Kind,
    Message,
    MessageCreateCommand,
    ServerEvent,
)


class Role(BaseModel):
    user_id: str


class Controller:
    """..."""

    def __init__(self, storage: Storage, agent: Agent) -> None:
        self.storage = storage
        self.agent = agent

    async def reply_to(self, message_id: str) -> Message:
        user_message = await self.storage.get_message(message_id)
        agent_message = await self.storage.create_message(user_message.conversation_id, "Agent")
        context = Context(self.storage, agent_message.id)
        await self.agent.reply_to(context)

    async def execute(self, role: Role, command: ClientCommand) -> None:
        # TODO check role
        # TODO should enter lock, to ensure sequential execution
        match command:
            case ConversationCreateCommand(title=title):
                _ = await self.storage.create_conversation(title)
            case MessageCreateCommand(conversation_id=conversation_id, content=content):
                user_name = role.user_id  # TODO get actual user name
                message = await self.storage.create_message(conversation_id, user_name)
                _ = await self.storage.create_fragment(message.id, None, Kind.NORMAL, content)
                # TODO agent reply should be handled in a more flexible location
                _ = await self.reply_to(message.id)
            case _:
                raise ValueError

    async def subscribe(self, role: Role) -> AsyncIterator[ServerEvent]:
        # TODO check role
        # TODO allow resuming from specific event id, to reduce bandwidth usage
        async for event in self.storage.subscribe():
            yield event
