"""Test user model and mixin."""
# Pyramid
import transaction

import pytest

# Websauna
from websauna.system.user.models import Group
from websauna.system.user.models import User
from websauna.utils import time


@pytest.fixture
def new_user(dbsession, new_group):
    """Create a new user and return it for testing."""
    with transaction.manager:
        u = User(email='example@example.com')
        u.groups.append(new_group)
        dbsession.add(u)
        dbsession.flush()
    return dbsession.query(User).get(1)


@pytest.fixture
def new_group(dbsession):
    """Create a new groups and return it for testing."""
    with transaction.manager:
        g = Group(name='Editors')
        dbsession.add(g)
    return dbsession.query(Group).get(1)


def test_user_creation(new_user):
    """Load the default user models and see we create corresponding tables right."""
    assert new_user.email == 'example@example.com'


def test_generate_username(new_user):
    """Test generate_username method."""
    assert new_user.generate_username() == 'user-1'


def test_friendly_name_with_email_fallback(new_user):
    """Test friendly_name property that will return the user email as fallback."""
    assert new_user.friendly_name == 'example@example.com'


def test_friendly_name_with_full_name(new_user):
    """Test friendly_name property that should return the full_name, if available."""
    new_user.full_name = 'Jarkko Oikarinen'
    assert new_user.friendly_name == 'Jarkko Oikarinen'


def test_friendly_name_with_username(new_user):
    """Test friendly_name property that should return the username, if available."""
    new_user.username = 'francois'
    assert new_user.friendly_name == 'francois'


def test_is_activated(new_user):
    """Test if user is activated (completed the email activation)."""
    assert new_user.is_activated() is False

    # Set activated_at
    new_user.activated_at = time.now()
    assert new_user.is_activated() is True


def test_can_login(new_user):
    """Test if user can login.

    User needs to be enabled and activated.
    """
    assert new_user.can_login() is False

    # Set activated_at
    new_user.activated_at = time.now()
    assert new_user.can_login() is True


def test_cannot_login_if_not_enable(new_user):
    """Test if setting enabled to false blocks user from login."""
    # Set activated_at
    new_user.activated_at = time.now()
    assert new_user.can_login() is True

    # Disable the user
    new_user.enabled = False
    assert new_user.can_login() is False


def test_user_is_in_group(dbsession, new_user):
    """Test if user is in a group."""
    new_user = dbsession.query(User).get(1)
    assert new_user.is_in_group('Editors') is True


def test_user_is_admin(dbsession, new_user):
    """Test if user is an admin."""
    new_user = dbsession.query(User).get(1)
    assert new_user.is_admin() is False

    with transaction.manager:
        g = Group(name='admin')
        dbsession.add(g)
    g = dbsession.query(Group).get(2)
    new_user.groups.append(g)

    assert new_user.is_admin() is True
