import asyncio

from openai import AsyncClient
from openai.types.chat import ChatCompletionMessageParam

from agent.client import Agent, Context, Controller
from agent.protocol import Kind


def build_chat_completion_messages(context: Context) -> list[ChatCompletionMessageParam]:
    current_message = context.workspace.messages[context.message_id]
    user_name = current_message.user_name
    conversation_id = current_message.conversation_id
    chat_messages = []
    for message in context.workspace.messages.values():
        if message.conversation_id == conversation_id:
            if message.user_name == user_name:
                role = "assistant"
            else:
                role = "user"
            for fragment in context.workspace.fragments.values():
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
        chat_completion_messages = build_chat_completion_messages(context)
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
    controller = Controller("ws://localhost:8080/", user_name, token, agent)
    await controller.run()


asyncio.run(main())
