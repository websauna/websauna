from pyramid_web20 import models

from pyramid_web20.tests import base

from pyramid_web20.models import DBSession


class TestLogin(base.DefaultModelBaseTest):
    """Stress database user model."""

    def setUp(self):
        """Create a sample user."""

    def test_user(self):
        user = models.User(username="miohtama")
        DBSession.add(user)
