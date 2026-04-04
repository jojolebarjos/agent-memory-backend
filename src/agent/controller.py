from collections.abc import AsyncIterator

from pydantic import BaseModel

from agent.storage import Storage

from .protocol import (
    ClientCommand,
    ConversationCreateCommand,
    Kind,
    MessageCreateCommand,
    ServerEvent,
)


class Role(BaseModel):
    user_id: str


class Controller:
    """Main controller.

    This is the entry point of external connectors.

    """

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

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
            case _:
                raise ValueError

    async def subscribe(self, role: Role) -> AsyncIterator[ServerEvent]:
        # TODO check role
        # TODO allow resuming from specific event id, to reduce bandwidth usage
        async for event in self.storage.subscribe():
            yield event
