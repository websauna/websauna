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
    """Create a non-conforming 128-bit random version 4 UUID.

    Random UUID is a RFC 4122 compliant UUID version 4 128-bit number. By default 6 fixed bits, 4 bits for version and 2 bits reserved for other purposes, are fixed. This function behaves like Python's ` uuid4()`` but also randomizes the remaining six bits, generating up to 128 bit randomness.

    This function also sources all bytes from `os.urandom()` to guarantee the randomness and security and does not rely operating system libraries.

    Using ``secure_uuid()`` poses a risk that generated UUIDs are not accepted when communicating with third party system. However, they are observed to be good for URLs and to be stored in PostgreSQL.

    More information

    * http://crypto.stackexchange.com/a/3525/25874

    * https://tools.ietf.org/html/rfc4122
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
