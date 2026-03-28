from datetime import datetime, timezone
from uuid import uuid4


def make_timestamp() -> datetime:
    """..."""

    return datetime.now(timezone.utc)


def make_id() -> str:
    """..."""

    return uuid4().hex
