from __future__ import annotations

from typing import TYPE_CHECKING

from agent.protocol import Kind


if TYPE_CHECKING:
    from agent.controller import Controller


class Context:
    """..."""

    def __init__(self, controller: Controller, message_id: str, fragment_id: str | None = None) -> None:
        self._controller = controller
        self._message_id = message_id
        self._fragment_id = fragment_id

    async def send(self, kind: Kind, content: str) -> Context:
        """..."""

        fragment = await self._controller.create_fragment(self._message_id, self._fragment_id, kind, content)
        return Context(self._controller, self._message_id, fragment.id)

    async def notify(self, kind: Kind, content: str) -> None:
        """..."""

        await self._controller.notify(kind, content)

    # TODO expose storage
