from .connection import Connection


class Client:
    def __init__(self, url: str) -> None:
        self._url = url

    def connect(self, since: str | None = None) -> Connection:
        return Connection(self._url, since)
