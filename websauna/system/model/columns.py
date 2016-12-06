"""Extra SQLAlchemy column declarations.

We have some sqlalchemy_utils aliasing here intenrally. In the future expect those aliases to be dropped in the favor of dropping sqlalchemy_utils dependency.
"""

import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB as _JSONB
from sqlalchemy.dialects.postgresql import INET as _INET
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.ip_address import IPAddressType
from sqlalchemy_utils.types.uuid import UUIDType


class UTCDateTime(DateTime):
    """An SQLAlchemy DateTime column which forces UTC timezone."""

    def __init__(self, *args, **kwargs):

        # If there is an explicit timezone we accept UTC only
        if "timezone" in kwargs:
            assert kwargs["timezone"] == datetime.timezone.utc

        kwargs = kwargs.copy()
        kwargs["timezone"] = datetime.timezone.utc
        super(UTCDateTime, self).__init__(**kwargs)

    def result_processor(self, dialect, coltype):

        import pdb ; pdb.set_trace()
        def process(value):
            if value is not None:
                value = bytes(value)
            return value

        return process


class JSONB(JSONType):
    """Generic JSONB type.

    Falls back to the native PostgreSQL JSONB type.
    """

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # Use the native JSON type.
            return dialect.type_descriptor(_JSONB())
        else:
            return dialect.type_descriptor(self.impl)


class INET(IPAddressType):
    """Generic IPv4/IPv6 type.

    Falls back to native PostgreSQL INET implementation.

    The resulting object is either :py:class:`ipaddress.IPv4Address` or :py:class:`ipaddress.IPv6Address`.
    """

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # Fallback to native PSQL INET
            return dialect.type_descriptor(_INET())
        else:
            return dialect.type_descriptor(self.impl)


class UUID(UUIDType):
    """Generic UUID type.

    Falls back to native PostgreSQL UUID implementation.

    The resulting object is :py:class:`uuid.UUID`.
    """
    
    def __init__(self, as_uuid=True):
        super(UUID, self).__init__(binary=True, native=True)


# Don't expose sqlalchemy_utils internals as they may go away
__all__ = [
    "UTCDateTime",
    "UUID",
    "JSONB",
    "INET",
]
