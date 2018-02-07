"""Tests for checking database sanity checks functions correctly."""

import datetime

# SQLAlchemy
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base

# Websauna
from websauna.system.model.columns import UTCDateTime

# pytest

import pytest


def test_UTCDateTime_restricts_timezone_to_utc():

    Base = declarative_base()

    class TestUTCModel(Base):
        """A sample SQLAlchemy model to demostrate db conflicts. """

        __tablename__ = "utc_datetime_test"

        date = Column(UTCDateTime(timezone=datetime.timezone.utc), primary_key=True)

    assert TestUTCModel.date.type.timezone is True

    with pytest.raises(ValueError):
        class TestUTCModel2(Base):
            """A sample SQLAlchemy model to demostrate db conflicts. """

            __tablename__ = "utc_datetime_test2"

            date = Column(UTCDateTime(timezone=object), primary_key=True)
