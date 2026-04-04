import asyncio
from functools import partial
from typing import Never

import click
from dotenv import load_dotenv
from websockets import ConnectionClosedOK, ServerConnection, serve

from agent.controller import Controller, Role
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

    storage = InMemoryStorage()
    controller = Controller(storage)

    asyncio.run(run(controller, host, port))


async def run(controller: Controller, host: str, port: int) -> None:

    await controller.storage.create_document(
        "unicorn",
        "Unicorn",
        ["fauna", "sentient", "fantasy"],
        "Encyclopedic description of unicorns",
        "The unicorn is a legendary creature that has been described since antiquity as a beast with a single large, pointed, spiraling horn projecting from its forehead.\n\nIn European literature and art, the unicorn has, for the last thousand years or so, been depicted as a white horse- or goat-like animal with a long, straight horn with spiraling grooves, cloven hooves, and sometimes a goat's beard. In the Middle Ages and Renaissance, it was commonly described as an extremely wild woodland creature, a symbol of purity and grace, which could be captured only by a virgin. In encyclopedias, its horn was described as having the power to render poisoned water potable and to heal sickness. In medieval and Renaissance times, the tusk of the $narwhal was sometimes sold as a unicorn horn.",
    )
    await controller.storage.create_document(
        "narwhal",
        "Narwhal",
        ["fauna"],
        "Encyclopedic description of narwhals",
        "The narwhal (Monodon monoceros) is a species of toothed whale native to the Arctic. It is the only member of the genus Monodon and one of two living representatives of the family Monodontidae. The narwhal is a stocky cetacean with a relatively blunt snout, a large melon, and a shallow ridge in place of a dorsal fin. Males of this species have a spiralled tusk that is 1.5–3.0 m (4.9–9.8 ft) long, which is a protruding left canine thought to function as a weapon, a tool for feeding, in attracting mates or sensing water salinity. Specially adapted slow-twitch muscles, along with the jointed neck vertebrae and shallow dorsal ridge allow for easy movement through the Arctic environment, where the narwhal spends extended periods at great depths. The narwhal's geographic range overlaps with that of the similarly built and closely related beluga whale, and the animals are known to interbreed.",
    )

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
