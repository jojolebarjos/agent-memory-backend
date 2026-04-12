import asyncio

import click
from dotenv import load_dotenv

from .controller import Controller
from .run import run
from .storage.in_memory import InMemoryStorage


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

    # TODO add argument to pick other storages
    storage = InMemoryStorage()
    controller = Controller(storage)

    asyncio.run(run(controller, host, port))


main()
