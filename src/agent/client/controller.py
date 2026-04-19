import asyncio
import time
from typing import Any, Coroutine

from agent.protocol import (
    ConversationCreatedEvent,
    DocumentCreatedEvent,
    FragmentCreatedEvent,
    Kind,
    Message,
    MessageCreatedEvent,
    MessageCreateRequest,
    MessageCreateResponse,
)
from agent.utility import make_id

from .agent import Agent
from .client import Client
from .context import Context
from .workspace import Workspace


class Controller:
    def __init__(self, uri: str, user_name: str, token: str, agent: Agent) -> None:
        self.uri = uri
        self.user_name = user_name
        self.token = token
        self.agent = agent
        self.workspace = Workspace()
        # TODO specify `since`, according to what we have on the disk
        self.client = Client(self.uri, self.token)
        self.conversation_callers = dict[str, DelayedCall]()

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        async with self.client:
            async for event in self.client:
                match event:
                    # TODO should maybe use WorkspaceSyncEvent to explicitly ignore initial messages?
                    case DocumentCreatedEvent(document=document):
                        self.workspace.documents[document.id] = document
                    case ConversationCreatedEvent(conversation=conversation):
                        assert conversation.id not in self.workspace.conversations
                        self.workspace.conversations[conversation.id] = conversation
                        self.conversation_callers[conversation.id] = DelayedCall(0.5)
                    case MessageCreatedEvent(message=message):
                        self.workspace.messages[message.id] = message
                    case FragmentCreatedEvent(fragment=fragment):
                        self.workspace.fragments[fragment.id] = fragment
                        if fragment.kind == Kind.END:
                            # Note: do not wait, on purpose
                            message = self.workspace.messages[fragment.message_id]
                            caller = self.conversation_callers[message.conversation_id]
                            loop.create_task(caller(self._reply_to(message.id)))

    async def _reply_to(self, previous_message_id: str) -> Message:
        previous_message = self.workspace.messages[previous_message_id]

        # Don't reply to our own messages
        if previous_message.user_name == self.user_name:
            return

        # Create message container
        request = MessageCreateRequest(
            request_id=make_id(),
            conversation_id=previous_message.conversation_id,
        )
        response = await self.client.send(request)
        assert isinstance(response, MessageCreateResponse)
        message = response.message

        # TODO hack, need the message already
        self.workspace.messages[message.id] = message

        # Ask agent to reply
        context = Context(self.client, self.workspace, message.id)
        start_time = time.perf_counter()
        # TODO catch exceptions
        await self.agent.reply_to(context)
        end_time = time.perf_counter()

        # Explicitly send END fragment
        _ = await context.create_fragment(Kind.END, f"Generated in {end_time - start_time:.01f}s")

        return message


class DelayedCall:
    def __init__(self, delay: float) -> None:
        self.delay = delay
        self.last_marker: Any = None

    async def __call__(self, coro: Coroutine) -> None:
        marker = object()
        self.last_marker = marker
        await asyncio.sleep(self.delay)
        if self.last_marker is marker:
            return await coro
        else:
            coro.close()
