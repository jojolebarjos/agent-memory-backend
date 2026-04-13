from collections.abc import AsyncIterator

from pydantic import BaseModel

from agent.protocol import (
    ClientRequest,
    ConversationCreateRequest,
    ConversationCreateResponse,
    DocumentCreateRequest,
    DocumentCreateResponse,
    FragmentCreateRequest,
    FragmentCreateResponse,
    MessageCreateRequest,
    MessageCreateResponse,
    ServerEvent,
    ServerResponse,
)

from .storage import Storage


class Role(BaseModel):
    user_id: str


class Controller:
    """Main controller.

    This is the entry point of external connectors.

    """

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    async def execute(self, role: Role, request: ClientRequest) -> ServerResponse:
        # TODO check role
        # TODO should enter lock, to ensure sequential execution
        match request:
            case DocumentCreateRequest(key=key, title=title, tags=tags, description=description, content=content):
                document = await self.storage.create_document(key, title, tags, description, content)
                return DocumentCreateResponse(request_id=request.request_id, document=document)
            case ConversationCreateRequest(title=title):
                conversation = await self.storage.create_conversation(title)
                return ConversationCreateResponse(request_id=request.request_id, conversation=conversation)
            case MessageCreateRequest(conversation_id=conversation_id):
                user_name = role.user_id  # TODO get actual user name
                message = await self.storage.create_message(conversation_id, user_name)
                return MessageCreateResponse(request_id=request.request_id, message=message)
            case FragmentCreateRequest(message_id=message_id, parent_id=parent_id, kind=kind, content=content):
                fragment = await self.storage.create_fragment(message_id, parent_id, kind, content)
                return FragmentCreateResponse(request_id=request.request_id, fragment=fragment)
            case _:
                raise ValueError

    async def subscribe(self, role: Role) -> AsyncIterator[ServerEvent]:
        # TODO check role
        # TODO allow resuming from specific event id, to reduce bandwidth usage
        async for event in self.storage.subscribe():
            yield event
