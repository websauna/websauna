"""Various Websauna specific py.test fixtures.

* Reading test.ini settings

* Setting up and tearing down database

* Creating a WSGI application to test
"""

# Standard Library
import os
import typing as t

# Pyramid
import plaster
import pyramid.testing
import transaction
from pyramid.interfaces import IRequest
from pyramid.paster import bootstrap
from pyramid.registry import Registry
from pyramid.router import Router

# SQLAlchemy
from sqlalchemy.orm.session import Session

import pytest

# Websauna
from websauna.system.devop.cmdline import setup_logging  # noQA
from websauna.system.http.utils import make_routable_request
from websauna.system.model.meta import create_dbsession
from websauna.tests.test_utils import make_dummy_request  # noQA
#: Make sure py.test picks this up
from websauna.tests.webserver import customized_web_server  # noQA
from websauna.tests.webserver import web_server  # noQA
from websauna.utils.qualname import get_qual_name


@pytest.fixture(scope='session')
def test_config_path(request) -> str:
    """A py.test fixture to get test INI configuration file path from py.test command line.

    :return: Absolute path to test.ini file
    """

    assert getattr(request.config.option, "ini", None), "You need to give --ini test.ini command line option to py.test to find our test settings"

    config_uri = os.path.abspath(request.config.option.ini)

    return config_uri


@pytest.fixture(scope='session')
def ini_settings(request, test_config_path) -> dict:
    """Load INI settings for test run from py.test command line.

    Example:

         py.test yourpackage -s --ini=test.ini


    :return: A dictionary representing the key/value pairs in an ``app`` section within the file represented by ``config_uri``
    """

    # Setup Python logging from the INI
    # Add Websauna loader
    if not test_config_path.startswith('ws://'):
        test_config_path = 'ws://{0}'.format(test_config_path)

    loader = plaster.get_loader(test_config_path)
    # Read [app] section
    settings = loader.get_settings('app:main')

    # To pass the config filename itself forward
    settings["_ini_file"] = test_config_path

    return settings


@pytest.fixture(scope='session')
def paster_config(request, test_config_path, ini_settings) -> tuple:
    """A fixture to get global config and app settings for Paster-like passing.

    This is mostly useful cases where your test needs to ramp up its own :py:class:`websauna.system.Initializer`.

    Example:

    .. code-block:: python

        def test_customize_login(paster_config):
            '''Customizing login form works.'''

            class CustomLoginForm(DefaultLoginForm):

                def __init__(self, *args, **kwargs):
                    login_button = Button(name="login_email", title="Login by fingerprint", css_class="btn-lg btn-block")
                    kwargs['buttons'] = (login_button,)
                    super().__init__(*args, **kwargs)

            class Initializer(websauna.system.Initializer):

                def configure_user_forms(self):

                    from websauna.system.user import interfaces

                    # This will set up all default forms as shown in websauna.system.Initializer.configure_user_forms
                    super(Initializer, self).configure_user_forms()

                    # Override the default login form with custom one
                    unregister_success= self.config.registry.unregisterUtility(provided=interfaces.ILoginForm)
                    assert unregister_success, "No default form register"
                    self.config.registry.registerUtility(CustomLoginForm, interfaces.ILoginForm)


            global_config, app_settings = paster_config
            init = Initializer(global_config, app_settings)
            init.run()
            app = TestApp(init.make_wsgi_app())
            resp = app.get("/login")
    """
    global_config = {"__file__": test_config_path}
    return global_config, ini_settings


def get_app(ini_settings: dict, extra_init: t.Optional[t.Callable] = None) -> Router:
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


@pytest.fixture(scope='session')
def init(request, app):
    """Access to the default :py:class:`websauna.system.Initializer` instance created from ``test.ini``.
    """
    return app.initializer


@pytest.fixture(scope='session')
def registry(request, app) -> Registry:
    """Get access to registry.

    Effectively returns ``app.initializer.config.registry``. Registry is a Pyramid registry that is populated with values from :ref:`test.ini`.

    Example:

    .. code-block:: python

        import transaction
        from websauna.tests.test_utils import create_user


        def test_some_stuff(dbsession, registry):

            with transaction.manager:
                u = create_user(registry)
                # Do stuff with new user

    """
    return app.initializer.config.registry


def create_test_dbsession(request, registry: Registry, transaction_manager=transaction.manager) -> Session:
    """Create a test database session and setup database.

    Create and drop all tables when called. Add teardown function py.test to drop all tables during teardown.
    Also add implicit UUID extension on the database, so we don't need to add by hand every time.

    :param request: py.test test request
    :param settings: test.ini app settings
    :param transaction_manager:
    :return: New database session
    """
    from websauna.system.model.meta import Base

    dbsession = create_dbsession(registry, manager=transaction_manager)
    engine = dbsession.get_bind()

    connection = engine.connect()

    # Support native PSQL UUID types
    if engine.dialect.name == "postgresql":
        connection.execute('create extension if not exists "uuid-ossp";')

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
    return create_test_dbsession(request, app.initializer.config.registry)


@pytest.fixture()
def http_request(request):
    """Dummy HTTP request for testing.

    For spoofing link generation, routing, etc.
    """
    request = pyramid.testing.DummyRequest()
    return request


@pytest.fixture()
def test_request(request, dbsession, registry) -> IRequest:
    """Create a dummy HTTP request object which can be used to obtain services and adapters.

    This fixture gives you an instance of :py:class:`pyramid.testing.DummyRequest` object which looks like a request as it would have arrived through HTTP interface. It has request-like properties, namely

    * registry

    * dbsession

    ... and thus can be used to access services, utilies and such which normally would take a request as an argument.

    Example:

    .. code-block:: python

        from websauna.system.user.utils import get_login_service


        def test_order(dbsession, test_request):
            service = get_login_service(test_request)

    The ``request.tm`` is bound to thread-local ``transaction.mananger``.
    """
    request = make_routable_request(dbsession, registry)
    request.tm = transaction.manager
    return request


@pytest.fixture
def scaffold_webdriver():
    """A fixture to get Webdriver settings from external environment to be used inside scaffold tests.

    TODO: This fixture does not serve purpose outside Websauna and should be moved somewhere.
    """
    # Workaround broken Firefox webdriver problem and allow use Chrome on OSX
    webdriver = os.environ.get("SPLINTER_WEBDRIVER")
    if webdriver:
        webdriver_param = "--splinter-webdriver=" + webdriver
    else:
        webdriver_param = ""
    return webdriver_param


def pytest_addoption(parser):
    parser.addoption("--ini", action="store", metavar="INI_FILE", help="use INI_FILE to configure SQLAlchemy")
