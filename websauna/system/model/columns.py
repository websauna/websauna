"""Extra SQLAlchemy column declarations.

We have some sqlalchemy_utils aliasing here intenrally. In the future expect those aliases to be dropped in the favor of dropping sqlalchemy_utils dependency.
"""

# Standard Library
import datetime

# SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy import types
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import INET as _INET
from sqlalchemy.exc import UnsupportedCompilationError
from sqlalchemy_utils.types.ip_address import IPAddressType
from sqlalchemy_utils.types.uuid import UUIDType


class UTCDateTime(DateTime):
    """An SQLAlchemy DateTime column that explicitly uses timezone aware dates and only accepts UTC."""

    def __init__(self, *args, **kwargs):
        # If there is an explicit timezone we accept UTC only
        if "timezone" in kwargs:
            if kwargs["timezone"] not in (datetime.timezone.utc, True):
                raise ValueError(
                    "Only 'datetime.timezone.utc' or True accepted"
                    " as timezone for '{}'".format(self.__class__.__name__)
                )

        kwargs = kwargs.copy()
        # Using an explict 'True' ensures no false positives
        # on alembic migrations due to failed equality test.
        # (issue #162)
        kwargs["timezone"] = True
        super(UTCDateTime, self).__init__(**kwargs)

    def _dialect_info(self, dialect):
        return super(UTCDateTime, self)._dialect_info(dialect)


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

    def __str__(self):
        """Printable info for this type.

        Override to avoid issues with logging raising an UnsupportedCompilationError here.
        :return: Representation of this type.
        """
        try:
            repr = str(self.compile())
        except UnsupportedCompilationError:
            dialect = self.impl._default_dialect()
            repr = str(self.compile(dialect=dialect))
        return repr


class UUID(UUIDType):
    """Generic UUID type.

    Falls back to native PostgreSQL UUID implementation.

    The resulting object is :py:class:`uuid.UUID`.
    """

    #: We force PSQL implementation by default here so that Alembic migration scripts don't do a column with unnecessary length attribute: sa.Column('uuid', websauna.system.model.columns.UUID(length=16), nullable=True),
    impl = postgresql.UUID()

    def __init__(self, as_uuid: bool=True):
        super(UUID, self).__init__(binary=True, native=True)

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql' and self.native:
            # Use the native UUID type.
            return dialect.type_descriptor(postgresql.UUID())
        else:
            # Fallback to either a BINARY or a CHAR.
            kind = types.BINARY(16)
            return dialect.type_descriptor(kind)


# Don't expose sqlalchemy_utils internals as they may go away
__all__ = [
    'UTCDateTime',
    'UUID',
    'INET',
]
