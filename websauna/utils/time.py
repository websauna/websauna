"""Time and date helpers."""
# Standard Library
import datetime


def now() -> datetime.datetime:
    """Get the current time as timezone-aware UTC timestamp.

    :return: Current datetime with UTC timezone
    """
    return datetime.datetime.now(datetime.timezone.utc)
