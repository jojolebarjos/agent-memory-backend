from agent.protocol import (
    Document,
    DocumentCreateRequest,
    DocumentCreateResponse,
    Fragment,
    FragmentCreateRequest,
    FragmentCreateResponse,
    Kind,
)
from agent.utility import make_id

from .client import Client
from .workspace import Workspace


class Context:
    """..."""

    def __init__(self, client: Client, workspace: Workspace, message_id: str) -> None:
        self.client = client
        self.workspace = workspace
        self.message_id = message_id

    async def create_fragment(self, kind: Kind, content: str, parent_id: str | None = None) -> Fragment:
        request = FragmentCreateRequest(
            request_id=make_id(),
            message_id=self.message_id,
            parent_id=parent_id,
            kind=kind,
            content=content,
        )
        response = await self.client.send(request)
        assert isinstance(response, FragmentCreateResponse)
        return response.fragment

    async def create_document(self, key: str, title: str, tags: list[str], description: str, content: str) -> Document:
        request = DocumentCreateRequest(
            request_id=make_id(),
            key=key,
            title=title,
            tags=tags,
            description=description,
            content=content,
        )
        response = await self.client.send(request)
        assert isinstance(response, DocumentCreateResponse)
        return response.document
