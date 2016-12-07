"""Extra SQLAlchemy column declarations.

We have some sqlalchemy_utils aliasing here intenrally. In the future expect those aliases to be dropped in the favor of dropping sqlalchemy_utils dependency.
"""

import datetime

from sqlalchemy import types
from sqlalchemy import DateTime
from sqlalchemy import processors
from sqlalchemy.dialects.postgresql import JSONB as _JSONB
from sqlalchemy.dialects.postgresql import INET as _INET
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.ip_address import IPAddressType
from sqlalchemy_utils.types.uuid import UUIDType
from sqlalchemy.dialects.sqlite import DATETIME as DATETIME_
from sqlalchemy.dialects import postgresql


class UTCDateTime(DateTime):
    """An SQLAlchemy DateTime column that explicitly uses timezone aware dates and only accepts UTC."""

    def __init__(self, *args, **kwargs):
        # If there is an explicit timezone we accept UTC only
        if "timezone" in kwargs:
            assert kwargs["timezone"] == datetime.timezone.utc

        kwargs = kwargs.copy()
        kwargs["timezone"] = datetime.timezone.utc
        super(UTCDateTime, self).__init__(**kwargs)

    def _dialect_info(self, dialect):
        if dialect.name == "sqlite":
            # Becase SQLite does not support datetimes, we need to explicitly tell here to use our super duper DATETIME() hack subclass that hacks in timezone
            return {"impl": SQLITEDATETIME()}
        else:
            return super(UTCDateTime, self)._dialect_info(dialect)


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

    #: We force PSQL implementation by default here so that Alembic migration scripts don't do a column with unnecessary length attribute: sa.Column('uuid', websauna.system.model.columns.UUID(length=16), nullable=True),
    impl = postgresql.UUID()
    
    def __init__(self, as_uuid=True):
        super(UUID, self).__init__(binary=True, native=True)

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql' and self.native:
            # Use the native UUID type.
            return dialect.type_descriptor(postgresql.UUID())
        else:
            # Fallback to either a BINARY or a CHAR.
            kind = types.BINARY(16)
            return dialect.type_descriptor(kind)


class SQLITEDATETIME(DATETIME_):
    """Timezone aware datetime support for SQLite.

    This is implementation used for UTCDateTime.
    """

    @staticmethod
    def process(value):
        dt = processors.str_to_datetime(value)
        if dt:
            # Returns naive datetime, force it to UTC
            return dt.replace(tzinfo=datetime.timezone.utc)
        return dt

    def result_processor(self, dialect, coltype):
        return SQLITEDATETIME.process


# Don't expose sqlalchemy_utils internals as they may go away
__all__ = [
    "UTCDateTime",
    "UUID",
    "JSONB",
    "INET",
]
