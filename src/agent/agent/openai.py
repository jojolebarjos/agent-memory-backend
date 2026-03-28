from typing import override

from openai import AsyncOpenAI

from agent.context import Context

from .base import Agent


class OpenAIAgent(Agent):
    """..."""

    def __init__(self, client: AsyncOpenAI, model: str) -> None:
        self.client = client
        self.model = model

    @override
    async def reply_to(self, context: Context) -> None:
        raise NotImplementedError
