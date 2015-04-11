import os
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base

import transaction

from pyramid import testing

import pytest

from . import fixture
from .. import models

TEST_DATABASE_NAME = "pyramid_web20_test"



@pytest.mark.usefixtures("ini_settings")
class DefaultModelBaseTest(unittest.TestCase):

    def setup_method(self, method):
        self._patchers = []
        self.config = testing.setUp()

    def add_patcher(self, patcher):
        self._patchers.append(patcher)
        patcher.start()
        return patcher

    def teardown_method(self, method):
        transaction.abort()
        testing.tearDown()

        for patcher in self._patchers:
            patcher.stop()

    def create_engine(self):
        """Get a hold of correct database depending on where tests are run."""

        # createdb unittest-conflict-resolution on homebrew based installations
        if "CI" in os.environ:
            # Running on Drone.IO
            engine = create_engine('postgresql://postgres@localhost/{}'.format(TEST_DATABASE_NAME))
        else:
            # Running locally
            engine = create_engine('postgresql:///{}'.format(TEST_DATABASE_NAME))

        return engine


def setup_sample_users(self):
    """Test case with two sample users with predefined details.

    - user, user2

    - Password is x
    """

    self.user = models.User(username="user", email="user@example.com")
    self.user.set_password("x")
    DBSession.add(user)

    self.user2 = models.User(username="user2", email="user2@example.com")
    self.user2.set_password("x")
    DBSession.add(user)

