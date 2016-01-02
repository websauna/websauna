"""Extra SQLAlchemy column declarations."""
import datetime

from sqlalchemy import DateTime


class UTCDateTime(DateTime):
    """An SQLAlchemy DateTime column which forces UTC timezone."""

    def __init__(self, *args, **kwargs):

        # If there is an explicit timezone we accept UTC only
        if "timezone" in kwargs:
            assert kwargs["timezone"] == datetime.timezone.utc

        kwargs = kwargs.copy()
        kwargs["timezone"] = datetime.timezone.utc
        super(UTCDateTime, self).__init__(**kwargs)
