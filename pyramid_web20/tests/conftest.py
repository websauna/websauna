"""Support for reading Pyramid configuration files and having rollbacked transactions in tests.

https://gist.github.com/inklesspen/4504383
"""


import os

import pyramid.testing

import pytest
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid_web20 import get_init
from pyramid_web20.models import DBSession
from pyramid_web20.models import Base


@pytest.fixture(scope='session')
def ini_settings(request):
    """Load INI settings from py.test command line."""

    if not getattr(request.config.option, "ini", None):
        raise RuntimeError("You need to give --ini test.ini command line option to py.test to find our test settings")

    from pyramid_web20.utils.configincluder import monkey_patch_paster_config_parser
    monkey_patch_paster_config_parser()

    config_uri = os.path.abspath(request.config.option.ini)
    setup_logging(config_uri)
    config = get_appsettings(config_uri)

    # To pass forward in fixtures
    config["_ini_file"] = config_uri

    return config


@pytest.fixture(scope='function')
def test_case_ini_settings(request):
    """Pass INI settings to a test class as self.config."""
    config = ini_settings(request)
    request.instance.config = config
    return config


@pytest.fixture(scope='session')
def init(request, ini_settings):
    """Load Pyramid web 2.0 Initializer, but do not run it."""
    if not getattr(request.config.option, "ini", None):
        raise RuntimeError("You need to give --ini test.ini command line option to py.test to find our test settings")

    init = get_init(dict(__file__=ini_settings["_ini_file"]), ini_settings)
    init.run(ini_settings)
    return init


@pytest.fixture(scope='session')
def sqlengine(request, init):

    engine = init.engine

    # Make sure we don't have any old data left from the last run
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def teardown():
        # There might be open transactions in the database. They will block DROP ALL and thus the tests would end up in a deadlock. Thus, we clean up all connections we know about.
        DBSession.close()
        Base.metadata.drop_all()

    request.addfinalizer(teardown)
    return engine


@pytest.fixture()
def dbtransaction(request, sqlengine):
    """Test runs within a single db transaction.

    The transaction is rolled back at the end of the test.
    """
    connection = sqlengine.connect()
    transaction = connection.begin()  # noqa
    DBSession.configure(bind=connection)

    def teardown():
        #connection.close()
        transaction.abort()
        DBSession.remove()

    request.addfinalizer(teardown)

    return connection


@pytest.fixture()
def dbsession(request, init):
    """Get a database session where we have initialized user models.

    Tables are purged after the run.
    """
    DBSession.close()

    with transaction.manager:
        Base.metadata.drop_all(init.engine)
        Base.metadata.create_all(init.engine)


    def teardown():
        # There might be open transactions in the database. They will block DROP ALL and thus the tests would end up in a deadlock. Thus, we clean up all connections we know about.
        # XXX: Fix this shit

        with transaction.manager:
            Base.metadata.drop_all(init.engine)

        DBSession.close()
        pass

    request.addfinalizer(teardown)

    return DBSession


@pytest.fixture()
def http_request(request):
    """Dummy HTTP request for testing.

    For spoofing link generation, routing, etc.
    """
    request = pyramid.testing.DummyRequest()
    return request




@pytest.fixture()
def pyramid_testing(request, ini_settings):
    """py.test fixture for ramping up Pyramid testing environment.

    :param request: py.test request lifecycle
    :param ini_settings: Fixture for command line passed --ini settings
    :return: {registry}
    """

    import pyramid.testing

    init = get_init(dict(__file__=ini_settings["_ini_file"]), ini_settings)
    init.run(ini_settings)

    pyramid.testing.setUp(registry=init.config.registry)

    def teardown():
        # There might be open transactions in the database. They will block DROP ALL and thus the tests would end up in a deadlock. Thus, we clean up all connections we know about.
        # XXX: Fix this shit
        pyramid.testing.tearDown()

    request.addfinalizer(teardown)

    return {"registry": init.config.registry}

#: Make sure py.test picks this up
from pyramid_web20.tests.functional import web_server  # noqa
from pyramid_web20.tests.functional import light_web_server  # noqa


def pytest_addoption(parser):
    parser.addoption("--ini", action="store", metavar="INI_FILE", help="use INI_FILE to configure SQLAlchemy")



