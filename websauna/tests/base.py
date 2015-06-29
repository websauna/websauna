import os
import unittest

from sqlalchemy import create_engine

import transaction

from pyramid import testing

import pytest


TEST_DATABASE_NAME = "websauna_test"



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
