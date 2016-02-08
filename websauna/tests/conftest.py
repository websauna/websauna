"""Support for reading Pyramid configuration files and having rollbacked transactions in tests.

https://gist.github.com/inklesspen/4504383
"""


import os
import pyramid.testing
import pytest
import transaction
from pyramid.router import Router

from sqlalchemy.orm.session import Session

from pyramid.paster import (
    get_appsettings,
    bootstrap)

from websauna.system.devop.cmdline import setup_logging
from websauna.system.model.meta import create_dbsession

# TODO: Remove this method
from websauna.compat.typing import Optional
from websauna.compat.typing import Callable
from websauna.utils.qualname import get_qual_name


@pytest.fixture(scope='session')
def test_config_path(request) -> str:
    """A py.test fixture to get test INI configuration file path from py.test command line."""

    assert getattr(request.config.option, "ini", None), "You need to give --ini test.ini command line option to py.test to find our test settings"

    config_uri = os.path.abspath(request.config.option.ini)

    return config_uri


@pytest.fixture(scope='session')
def ini_settings(request, test_config_path) -> dict:
    """Load INI settings for test run from py.test command line.

    Example:

         py.test yourpackage -s --ini=test.ini


    :return: Adictionary representing the key/value pairs in an ``app`` section within the file represented by ``config_uri``
    """

    from websauna.utils.configincluder import monkey_patch_paster_config_parser
    monkey_patch_paster_config_parser()

    setup_logging(test_config_path)
    config = get_appsettings(test_config_path)

    # To pass the config filename itself forward
    config["_ini_file"] = test_config_path

    return config


def get_app(ini_settings: dict, extra_init: Optional[Callable] = None) -> Router:
    """Construct a WSGI application from INI settings.

    You can pass extra callable which is called back when Initializer is about to finish. This allows you to poke app configuration easily.
    """
    if extra_init:
        # Convert extra init to string, because Paster stack doesn't allow raw objects through configuration
        options = {"extra_init": get_qual_name(extra_init)}
    else:
        options = None

    data = bootstrap(ini_settings["_ini_file"], options=options)
    return data["app"]



@pytest.fixture(scope='session')
def app(request, ini_settings: dict, **settings_overrides) -> Router:
    """Initialize WSGI application from INI file given on the command line.

    :param settings_overrides: Override specific settings for the test case.

    :return: WSGI application instance as created by ``Initializer.make_wsgi_app()``. You can access the Initializer instance itself as ``app.initializer``.
    """
    if "_ini_file" not in ini_settings:
        raise RuntimeError("You need to give --ini test.ini command line option to py.test to find our test settings")

    data = bootstrap(ini_settings["_ini_file"])
    return data["app"]


@pytest.fixture(scope='function')
def test_case_ini_settings(request):
    """Pass INI settings to a test class as self.config."""
    config = ini_settings(request)
    request.instance.config = config
    return config


@pytest.fixture(scope='session')
def init(request, app):
    """Access to the default :py:class:`websauna.system.Initializer` instance created from ``test.ini``.
    """
    return app.initializer


@pytest.fixture(scope='session')
def registry(request, app):
    """Access registry of the default app instance created from ``test.ini``.

    """
    return app.initializer.config.registry


def custom_dbsession(request, app: Router, transaction_manager=transaction.manager) -> Session:
    from websauna.system.model.meta import Base

    dbsession = create_dbsession(app.initializer.config.registry.settings, manager=transaction_manager)
    engine = dbsession.get_bind()

    with transaction.manager:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def teardown():
        # There might be open transactions in the database. They will block DROP ALL and thus the tests would end up in a deadlock. Thus, we clean up all connections we know about.
        # XXX: Fix this shit

        with transaction.manager:
            Base.metadata.drop_all(engine)

        dbsession.close()

    request.addfinalizer(teardown)

    return dbsession



@pytest.fixture()
def dbsession(request, app) -> Session:
    """Create a test database and database session.

    Connect to the test database specified in test.ini. Create and destroy all tables by your Initializer configuration.

    Performs SQLAlchemy table initialization for all models connected to ``websauna.system.model.meta.Base``.
    You must do manual opening and closing transaction inside the test, preferably using ``transaction.manager`` context manager. If transaction is left open, subsequent tests may fail.

    Example::

        import transaction

        from trees.models import NewsletterSubscriber

        def test_subscribe_newsletter(dbsession):
            '''Visitor can subscribe to a newsletter.'''

            # ... test code goes here ...

            # Check we get an entry
            with transaction.manager:
                assert dbsession.query(NewsletterSubscriber).count() == 1
                subscription = dbsession.query(NewsletterSubscriber).first()
                assert subscription.email == "foobar@example.com"
                assert subscription.ip == "127.0.0.1"

    :return: A SQLAlchemy session instance you can use to query database.
    """
    return custom_dbsession(request, app)


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


@pytest.fixture()
def pyramid_request(request, init):
    """Get a gold of pyramid.testing.DummyRequest object."""
    from pyramid import testing

    testing.setUp(registry=init.config.registry)
    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)

    _request = testing.DummyRequest()
    return _request


#: Make sure py.test picks this up
from websauna.tests.webserver import web_server  # noqa
from websauna.tests.webserver import customized_web_server  # noqa

def pytest_addoption(parser):
    parser.addoption("--ini", action="store", metavar="INI_FILE", help="use INI_FILE to configure SQLAlchemy")



