from agent.protocol import Conversation, Document, Fragment, Message


# TODO improve this local storage!


class Workspace:
    """..."""

    def __init__(self) -> None:
        self.documents = dict[str, Document]()
        self.conversations = dict[str, Conversation]()
        self.messages = dict[str, Message]()
        self.fragments = dict[str, Fragment]()

    # TODO provide helpers
