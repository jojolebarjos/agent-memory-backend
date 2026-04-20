import asyncio

from openai import AsyncClient
from openai.types.chat import ChatCompletionMessageParam

from agent.client import Agent, Context, Controller, InMemoryStorage
from agent.protocol import Fragment, Kind, Message


def build_chat_completion_messages(
    current_message: Message,
    messages: list[Message],
    fragments: list[Fragment],
) -> list[ChatCompletionMessageParam]:
    user_name = current_message.user_name
    chat_messages = []
    # TODO should probably sort messages and fragments by timestamp
    for message in messages:
        if message.user_name == user_name:
            role = "assistant"
        else:
            role = "user"
        for fragment in fragments:
            if fragment.message_id == message.id:
                if fragment.kind == Kind.NORMAL:
                    chat_message = {
                        "role": role,
                        # TODO add "name"?
                        "content": fragment.content,
                    }
                    chat_messages.append(chat_message)
                # TODO handle other fragment kinds
    return chat_messages


class MyAgent(Agent):
    def __init__(self) -> None:
        self.client = AsyncClient()

    async def reply_to(self, context: Context) -> None:
        _, messages, fragments = await context.storage.get_conversation_data(context.message.conversation_id)
        chat_completion_messages = build_chat_completion_messages(context.message, messages, fragments)
        chat_completion = await self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=chat_completion_messages,
        )
        [choice] = chat_completion.choices
        assert choice.finish_reason == "stop"
        content = choice.message.content
        _ = await context.create_fragment(Kind.NORMAL, content)


async def main():
    agent = MyAgent()
    user_name = "agent"
    # TODO once token system is properly in place, use this instead of the user name
    token = user_name
    storage = InMemoryStorage()
    controller = Controller("ws://localhost:8080/", user_name, token, storage, agent)
    await controller.run()


asyncio.run(main())
