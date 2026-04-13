from types import TracebackType
from typing import Self

from websockets import ClientConnection, ConnectionClosed, connect

from agent.protocol import (
    ClientRequest,
    ConversationCreateRequest,
    DocumentCreateRequest,
    FragmentCreateRequest,
    Kind,
    MessageCreateRequest,
    ServerEvent,
    server_event_adapter,
)


class Connection:
    def __init__(self, url: str, since: str | None) -> None:
        self._url = url
        self._since = since  # TODO: pass to server during handshake once event replay is supported
        self._ws: ClientConnection

    async def __aenter__(self) -> Self:
        self._ws = await connect(self._url)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._ws.close()

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> ServerEvent:
        try:
            payload = await self._ws.recv()
            return server_event_adapter.validate_json(payload)
        except ConnectionClosed:
            raise StopAsyncIteration

    async def send(self, command: ClientRequest) -> None:
        await self._ws.send(command.model_dump_json())

    async def create_conversation(self, title: str) -> None:
        await self.send(ConversationCreateRequest(title=title))

    async def create_message(self, conversation_id: str) -> None:
        await self.send(MessageCreateRequest(conversation_id=conversation_id))

    async def create_fragment(self, message_id: str, kind: Kind, content: str, parent_id: str | None = None) -> None:
        await self.send(FragmentCreateRequest(message_id=message_id, parent_id=parent_id, kind=kind, content=content))

    async def create_document(self, key: str, title: str, tags: list[str], description: str, content: str) -> None:
        await self.send(
            DocumentCreateRequest(key=key, title=title, tags=tags, description=description, content=content)
        )
