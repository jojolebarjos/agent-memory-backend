from agent.protocol import Fragment, FragmentCreateRequest, FragmentCreateResponse, Kind
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

    # TODO create document

    # TODO notify
