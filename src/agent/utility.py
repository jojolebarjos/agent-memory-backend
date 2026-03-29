from datetime import datetime, timezone
from uuid import uuid4


def make_timestamp() -> datetime:
    """Generate timezone-aware timestamp."""

    return datetime.now(timezone.utc)


def make_id() -> str:
    """Generate random unique identifier."""

    return str(uuid4())
