"""Tests UTC datetime."""

# Standard Library
import datetime

# Pyramid
import transaction

# SQLAlchemy
from sqlalchemy.exc import StatementError

import pytest

# Websauna
from websauna.system.model.columns import UTCDateTime
from websauna.system.user.models import User


def test_user_created_at_is_UTCDateTime():
    assert isinstance(User.created_at.type, UTCDateTime)
    assert User.created_at.type.timezone is True


def test_UTCDateTime_set_utc_timezone(dbsession):
    # Create a datetime naive instance
    naive_now = datetime.datetime.now()

    with transaction.manager:
        u = User(email='amazinguser@example.com')
        u.last_login_at = naive_now
        dbsession.add(u)
        dbsession.flush()

    user = dbsession.query(User).get(1)
    assert user.last_login_at.tzinfo == datetime.timezone.utc


def test_UTCDateTime_keep_timezone_info(dbsession):
    utc_now = datetime.datetime.utcnow()

    with transaction.manager:
        u = User(email='amazinguser@example.com')
        u.last_login_at = utc_now
        dbsession.add(u)
        dbsession.flush()

    user = dbsession.query(User).get(1)
    assert user.last_login_at.tzinfo == datetime.timezone.utc


def test_UTCDateTime_raises_type_error_with_wrong_input(dbsession):
    not_datetime = '2018-12-21T20:55:00+01:00'

    with pytest.raises(StatementError) as exc_info:
        u = User(email='amazinguser@example.com')
        u.last_login_at = not_datetime
        dbsession.add(u)
        dbsession.flush()

    original_exc = exc_info.value.orig
    assert isinstance(original_exc, TypeError)
    assert str(original_exc) == "expected datetime.datetime, not '2018-12-21T20:55:00+01:00'"
