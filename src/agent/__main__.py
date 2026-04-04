import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Never

import click
from dotenv import load_dotenv
from openai import AsyncOpenAI
from websockets import ConnectionClosedOK, ServerConnection, serve

from agent.agent.openai import OpenAIAgent
from agent.controller import Controller, Role
from agent.embedder.qwen3 import Qwen3Embedder
from agent.protocol import client_command_adapter
from agent.storage.in_memory import InMemoryStorage


@click.command()
@click.option(
    "-h",
    "--host",
    default="localhost",
    help="Host name",
)
@click.option(
    "-p",
    "--port",
    type=int,
    default=8080,
    help="Host port",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable DEBUG logs.",
)
def main(host: str, port: int, verbose: bool) -> None:
    """Run WebSocket server."""

    load_dotenv()
    asyncio.run(run(host, port))


async def run(host: str, port: int) -> None:
    executor = ThreadPoolExecutor()
    embedder = Qwen3Embedder(executor)
    storage = InMemoryStorage(embedder)
    client = AsyncOpenAI()
    agent = OpenAIAgent(client, model="gpt-4.1-nano")
    controller = Controller(storage, agent)
    async with serve(partial(handle, controller=controller), host, port) as _:
        await asyncio.Future()


async def handle(connection: ServerConnection, controller: Controller) -> None:
    authorization = connection.request.headers.get("Authorization")
    if authorization is not None:
        # TODO check JWT
        raise NotImplementedError
    else:
        user_id = "guest"
    role = Role(user_id=user_id)
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(incoming_loop(connection, controller, role))
            group.create_task(outgoing_loop(connection, controller, role))
    except* ConnectionClosedOK:
        pass


async def incoming_loop(connection: ServerConnection, controller: Controller, role: Role) -> Never:
    while True:
        payload = await connection.recv()
        command = client_command_adapter.validate_json(payload)
        await controller.execute(role, command)


async def outgoing_loop(connection: ServerConnection, controller: Controller, role: Role) -> Never:
    async for event in controller.subscribe(role):
        payload = event.model_dump_json()
        await connection.send(payload)
    raise RuntimeError("Event stream closed")


main()
