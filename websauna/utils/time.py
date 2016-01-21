"""Time and date helpers."""

import datetime


def now() -> datetime.datetime:
    """Get the current time as timezone-aware UTC timestamp."""
    return datetime.datetime.now(datetime.timezone.utc)