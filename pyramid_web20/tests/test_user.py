from .base import BaseTest
from . import fixtures as fix

from .. import models


class TestUser(BaseTest):
    """Stress database user model."""

    def test_user(self):
        user = models.User.create(username="miohtama")
        user.save()
