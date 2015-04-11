from pyramid_web20 import models

from pyramid_web20.tests import base

from pyramid_web20.models import DBSession


class TestUser(base.DefaultUserBaseTest):
    """Stress database user model."""

    def test_user(self):

