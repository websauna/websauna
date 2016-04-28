"""Support for reading Pyramid configuration files and having rollbacked transactions in tests.

https://gist.github.com/inklesspen/4504383
"""


import os
import pyramid.testing
import pytest
import transaction
from pyramid.router import Router
from pytest_splinter.plugin import Browser

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
from websauna.utils.configincluder import IncludeAwareConfigParser


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

    # This enables our INI inclusion mechanism
    # TODO: Don't use get_appsettings() from paster, but create a INI includer compatible version
    from websauna.utils.configincluder import monkey_patch_paster_config_parser
    monkey_patch_paster_config_parser()

    # Setup Python logging from the INI
    setup_logging(test_config_path)

    # Read [app] section
    config = get_appsettings(test_config_path)

    # To pass the config filename itself forward
    config["_ini_file"] = test_config_path

    return config


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


@pytest.fixture
def browser(request, browser_instance_getter, ini_settings) -> Browser:
    """Websauna specic browser fixtures.

    This is a py.test fixture to create a :term:`pytest-splinter` based browser instance. It is configured with splinter settings from an INI ``[splinter]`` section.

    .. note ::

        These will override any command line options given.

    .. note ::

        This is a temporary mechanism and will be phased out with INI based configuration.

    Example in ``test.ini``::

        [splinter]
        make_screenshot_on_failure = false

    For list of possible settings see this function source code.

    More information

    * https://github.com/pytest-dev/pytest-splinter/blob/master/pytest_splinter/plugin.py
    """

    splinter_command_line_args = [
        "splinter_session_scoped_browser",
        "splinter_browser_load_condition",
        "splinter_browser_load_timeout",
        "splinter_download_file_types",
        "splinter_driver_kwargs",
        "splinter_file_download_dir",
        "splinter_firefox_profile_preferences",
        "splinter_firefox_profile_directory",
        "splinter_make_screenshot_on_failure",
        "splinter_remote_url",
        "splinter_screenshot_dir",
        "splinter_selenium_implicit_wait",
        "splinter_wait_time",
        "splinter_selenium_socket_timeout",
        "splinter_selenium_speed",
        "splinter_webdriver_executable",
        "splinter_window_size",
        "splinter_browser_class",
        "splinter_clean_cookies_urls",
    ]

    # Cache read settings on a function attribute
    full_config = getattr(browser, "full_config", None)
    if not full_config:
        parser = IncludeAwareConfigParser()
        parser.read(ini_settings["_ini_file"])
        full_config = browser.full_config = parser

    # If INI provides any settings override splinter defaults
    for arg in splinter_command_line_args:
        ini_setting_name = arg.replace("splinter_", "")
        # Read setting from splinter section
        arg_value = full_config.get("splinter", ini_setting_name, fallback=None)
        if arg_value:
            setattr(request.config.option, arg, arg_value)

    return browser_instance_getter(request, browser)



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


def create_test_dbsession(request, settings: dict, transaction_manager=transaction.manager) -> Session:
    """Create a test database session and setup database.

    Create and drop all tables when called. Add teardown function py.test to drop all tables during teardown.

    :param request: py.test test request
    :param settings: test.ini app settings
    :param transaction_manager:
    :return: New database session
    """
    from websauna.system.model.meta import Base

    dbsession = create_dbsession(settings, manager=transaction_manager)
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
    return create_test_dbsession(request, app.initializer.config.registry.settings)


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



