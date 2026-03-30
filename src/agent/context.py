from __future__ import annotations

from agent.protocol import Kind
from agent.storage import Storage


class Context:
    """Conversation context.

    This is the main entry-point to the current state for the agent.

    """

    def __init__(self, storage: Storage, message_id: str, fragment_id: str | None = None) -> None:
        self.storage = storage
        self.message_id = message_id
        self.fragment_id = fragment_id

    async def send(self, kind: Kind, content: str) -> Context:
        fragment = await self.storage.create_fragment(self.message_id, self.fragment_id, kind, content)
        return Context(self.storage, self.message_id, fragment.id)

    async def notify(self, kind: Kind, content: str) -> None:
        await self.storage.notify(kind, content)
