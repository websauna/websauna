from uuid import UUID
import os
import datetime

from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

#: TODO: How to handle the fact that Horus requires custom declarative base?
Base = declarative_base()


def now():
    """Get timezone-aware UTC timestamp."""
    return datetime.datetime.now(datetime.timezone.utc)


utc = datetime.timezone.utc

# Make sure we store all dateimes as UTC in the database by importing this SQLAlchemy type augmentator
from . import sqlalchemyutcdatetime  # noqa


def secure_uuid():
    """Create non-guessable UUID object.

    This is equal to ``uuid.uuid4()``, but we source all bytes from `os.urandom()` to guarantee the randomness and security.
    """
    return UUID(bytes=os.urandom(16), version=4)


class UTCDateTime(DateTime):
    """An SQLAlchemy DateTime column which forces UTC timezone."""

    def __init__(self, *args, **kwargs):

        # If there is an explicit timezone we accept UTC only
        if "timezone" in kwargs:
            assert kwargs["timezone"] == utc

        kwargs = kwargs.copy()
        kwargs["timezone"] = utc
        super(UTCDateTime, self).__init__(**kwargs)
