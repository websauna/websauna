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
    setup_logging,
    bootstrap)

# TODO: Remove this method
from websauna.system import get_init
from websauna.system.model.meta import create_dbsession


@pytest.fixture(scope='session')
def ini_settings(request) -> dict:
    """Load INI settings for test run from py.test command line.

    Example:

         py.test yourpackage -s --ini=test.ini


    :return: Adictionary representing the key/value pairs in an ``app`` section within the file represented by ``config_uri``
    """

    if not getattr(request.config.option, "ini", None):
        raise RuntimeError("You need to give --ini test.ini command line option to py.test to find our test settings")

    from websauna.utils.configincluder import monkey_patch_paster_config_parser
    monkey_patch_paster_config_parser()

    config_uri = os.path.abspath(request.config.option.ini)
    setup_logging(config_uri)
    config = get_appsettings(config_uri)

    # To pass the config filename itself forward
    config["_ini_file"] = config_uri

    return config


@pytest.fixture(scope='session')
def app(request, ini_settings, **settings_overrides):
    """Initialize WSGI application from INI file given on the command line.

    TODO: This can be run only once per testing session, as SQLAlchemy does some stupid shit on import, leaks globals and if you run it again it doesn't work. E.g. trying to manually call ``app()`` twice::

         Class <class 'websauna.referral.models.ReferralProgram'> already has been instrumented declaratively

    :param settings_overrides: Override specific settings for the test case.

    :return: WSGI application instance as created by ``Initializer.make_wsgi_app()``. You can access the Initializer instance itself as ``app.initializer``.
    """
    if not getattr(request.config.option, "ini", None):
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
    """Backwards compatibility.

    TODO: Remove this fixture, use app
    """
    return app.initializer


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



