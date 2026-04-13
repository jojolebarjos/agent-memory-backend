from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, TypeAdapter
from pydantic.alias_generators import to_camel


class Kind(StrEnum):
    NORMAL = "normal"
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class _Base(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class Document(_Base):
    id: str
    created_at: AwareDatetime
    # TODO workspace_id
    key: str
    version: int
    title: str
    tags: list[str]
    description: str
    content: str


class Conversation(_Base):
    id: str
    created_at: AwareDatetime
    # TODO workspace_id
    title: str


class Message(_Base):
    id: str
    created_at: AwareDatetime
    conversation_id: str
    user_name: str


class Fragment(_Base):
    id: str
    created_at: AwareDatetime
    message_id: str
    parent_id: str | None = None
    kind: Kind
    content: str


class WorkspaceSyncEvent(_Base):
    type: Literal["workspace.sync"] = "workspace.sync"
    count: int


class DocumentCreatedEvent(_Base):
    type: Literal["document.created"] = "document.created"
    document: Document


class ConversationCreatedEvent(_Base):
    type: Literal["conversation.created"] = "conversation.created"
    conversation: Conversation


class MessageCreatedEvent(_Base):
    type: Literal["message.created"] = "message.created"
    message: Message


class FragmentCreatedEvent(_Base):
    type: Literal["fragment.created"] = "fragment.created"
    fragment: Fragment


class NotificationEvent(_Base):
    type: Literal["notification"] = "notification"
    kind: Kind
    content: str


ServerEvent = Annotated[
    WorkspaceSyncEvent
    | DocumentCreatedEvent
    | ConversationCreatedEvent
    | MessageCreatedEvent
    | FragmentCreatedEvent
    | NotificationEvent,
    Field(discriminator="type"),
]


class DocumentCreateResponse(_Base):
    type: Literal["document.create.response"] = "document.create.response"
    request_id: str
    document: Document


class ConversationCreateResponse(_Base):
    type: Literal["conversation.create.response"] = "conversation.create.response"
    request_id: str
    conversation: Conversation


class MessageCreateResponse(_Base):
    type: Literal["message.create.response"] = "message.create.response"
    request_id: str
    message: Message


class FragmentCreateResponse(_Base):
    type: Literal["fragment.create.response"] = "fragment.create.response"
    request_id: str
    fragment: Fragment


ServerResponse = Annotated[
    DocumentCreateResponse | ConversationCreateResponse | MessageCreateResponse | FragmentCreateResponse,
    Field(discriminator="type"),
]


class DocumentCreateRequest(_Base):
    type: Literal["document.create"] = "document.create"
    request_id: str
    key: str
    title: str
    tags: list[str]
    description: str
    content: str


class ConversationCreateRequest(_Base):
    type: Literal["conversation.create"] = "conversation.create"
    request_id: str
    title: str


class MessageCreateRequest(_Base):
    type: Literal["message.create"] = "message.create"
    request_id: str
    conversation_id: str


class FragmentCreateRequest(_Base):
    type: Literal["fragment.create"] = "fragment.create"
    request_id: str
    message_id: str
    parent_id: str | None = None
    kind: Kind
    content: str


ClientRequest = Annotated[
    ConversationCreateRequest | MessageCreateRequest | FragmentCreateRequest | DocumentCreateRequest,
    Field(discriminator="type"),
]

client_request_adapter = TypeAdapter[ClientRequest](ClientRequest)
server_event_adapter = TypeAdapter[ServerEvent](ServerEvent)
