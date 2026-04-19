from agent.protocol import (
    ConversationCreatedEvent,
    DocumentCreatedEvent,
    FragmentCreatedEvent,
    Kind,
    Message,
    MessageCreatedEvent,
    MessageCreateRequest,
    MessageCreateResponse,
    WorkspaceSyncEvent,
)
from agent.utility import make_id

from .agent import Agent
from .client import Client
from .context import Context
from .workspace import Workspace


class Watcher:
    def __init__(self, uri: str, token: str, agent: Agent) -> None:
        self.uri = uri
        self.token = token
        self.agent = agent
        self.workspace = Workspace()
        # TODO specify `since`, according to what we have on the disk
        self.client = Client(self.uri, self.token)

    async def run(self) -> None:
        async with self.client:
            async for event in self.client:
                # TODO update storage
                match event:
                    case WorkspaceSyncEvent(count=_count):
                        # TODO
                        pass
                    case DocumentCreatedEvent(document=document):
                        self.workspace.documents[document.id] = document
                    case ConversationCreatedEvent(conversation=conversation):
                        self.workspace.conversations[conversation.id] = conversation
                    case MessageCreatedEvent(message=message):
                        self.workspace.messages[message.id] = message
                    case FragmentCreatedEvent(fragment=fragment):
                        self.workspace.fragments[fragment.id] = fragment
                        if fragment.kind == Kind.END:
                            # TODO should only trigger this if there are not any response already
                            _ = await self._reply_to(fragment.message_id)

    async def _reply_to(self, message_id: str) -> Message:
        previous_message = self.workspace.messages[message_id]

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
        # TODO catch exceptions
        await self.agent.reply_to(context)

        # Explicitly send END fragment
        _ = await context.create_fragment(Kind.END, "Generated in 1.2s")

        return message
