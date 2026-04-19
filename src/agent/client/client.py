import asyncio
from asyncio import Future, Queue, Task
from collections.abc import AsyncIterator
from typing import Self

from websockets import ClientConnection, ConnectionClosed, connect

from agent.protocol import ClientRequest, ServerEvent, ServerResponse, server_payload_adapter


class Client:
    """..."""

    def __init__(self, url: str, token: str, since: str | None = None) -> None:
        self.url = url
        self.token = token
        self.since = since
        self.connection: ClientConnection | None = None
        self.task: Task | None = None
        self.queue = Queue[ServerEvent]()
        self.pending_requests = dict[str, Future]()

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __aiter__(self) -> AsyncIterator[ServerEvent]:
        return self

    async def __anext__(self) -> ServerEvent:
        return await self.queue.get()

    async def open(self) -> None:
        assert self.connection is None
        assert self.task is None
        self.connection = await connect(
            self.url,
            additional_headers={"Authorization": f"Bearer {self.token}"},
        )
        try:
            self.task = asyncio.create_task(self._incoming_loop())
            # TODO handshake including sync
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        if self.task is not None:
            self.task.cancel()
            self.task = None
        # TODO maybe add sentry in queue, to mark end of stream?

    async def _incoming_loop(self) -> None:
        try:
            while True:
                data = await self.connection.recv()
                # TODO improve this
                payload = server_payload_adapter.validate_json(data)
                if hasattr(payload, "request_id"):
                    future = self.pending_requests.pop(payload.request_id)
                    future.set_result(payload)
                else:
                    await self.queue.put(payload)
        except ConnectionClosed:
            pass

    async def send(self, request: ClientRequest) -> ServerResponse:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        assert request.request_id not in self.pending_requests
        data = request.model_dump_json()
        await self.connection.send(data)
        self.pending_requests[request.request_id] = future
        # TODO should have some timeout
        return await future
