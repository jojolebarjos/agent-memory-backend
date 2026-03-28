from contextlib import AbstractAsyncContextManager


class Context:
    def __init__(self):
        # TODO expose
        pass

    async def send(self) -> AbstractAsyncContextManager:
        pass
