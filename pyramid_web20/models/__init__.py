import datetime

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
