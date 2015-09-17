"""py.test fixtures for spinning up a WSGI server for functional test run."""

import threading
import time
from pyramid.router import Router
from waitress import serve
from urllib.parse import urlparse

import pytest

from backports import typing

#: The URL where WSGI server is run from where Selenium browser loads the pages
HOST_BASE = "http://localhost:8521"


class ServerThread(threading.Thread):
    """Run WSGI server on a background thread.

    This thread starts a web server for a given WSGI application. Then the Selenium WebDriver can connect to this web server, like to any web server, for running functional tests.
    """

    def __init__(self, app:Router, hostbase:str=HOST_BASE):
        threading.Thread.__init__(self)
        self.app = app
        self.srv = None
        self.daemon = True
        self.hostbase = hostbase

    def run(self):
        """Start WSGI server on a background to listen to incoming."""
        parts = urlparse(self.hostbase)
        domain, port = parts.netloc.split(":")

        try:
            # TODO: replace this with create_server call, so we can quit this later
            # log_socket_errors -> when Selenium WebDriver quits it may uncleanly stop ongoing Firefox HTTP requests, spitting out stuff to console
            serve(self.app, host='127.0.0.1', port=int(port), log_socket_errors=False, _quiet=True)
        except Exception as e:
            # We are a background thread so we have problems to interrupt tests in the case of error. Try spit out something to the console.
            import traceback
            traceback.print_exc()

    def quit(self):
        """Stop test webserver."""

        # waitress has no quit

        # if self.srv:
        #    self.srv.shutdown()


@pytest.fixture(scope='session')
def web_server(request, app) -> str:
    """py.test fixture to create a WSGI web server for functional tests.

    :param app: py.test fixture for constructing a WSGI application

    :return: localhost URL where the web server is running.
    """

    server = ServerThread(app)
    server.start()

    # Wait randomish time to allows SocketServer to initialize itself.
    # TODO: Replace this with proper event telling the server is up.
    time.sleep(0.1)

    # assert server.srv is not None, "Could not start the test web server"

    host_base = HOST_BASE

    def teardown():
        server.quit()

    request.addfinalizer(teardown)
    return host_base



_customized_web_server_port = 8522

@pytest.fixture()
def customized_web_server(request, app) -> typing.Callable:
    '''py.test fixture to create a WSGI web server for functional tests with custom INI options set.

    This is similar to ``web_server``, but instead directly spawning a server, it returns a factory method which you can use to launch the web server which custom parameters besides those given in test.ini.

    Example::

        def test_newsletter_splash(DBSession, customized_web_server, browser):
            """All visitors get a newsletter subscription dialog when arriving to the landing page.

            :param dbsession: py.test fixture for
            :param ini_settings: py.test fixture for loading INI settings from command line
            """

            # Create a WSGI server where newsletter splash dialog is explicitly enabled (disabled by default for testing)
            web_server = customized_web_server({"trees.newsletter_splash": True})

            b = browser
            b.visit(web_server)

            # Scroll down a bit to trigger the dialog
            browser.driver.execute_script("window.scrollTo(0, 10)")

            # Wait the dialog to come up
            time.sleep(2)

    Another example where we create one web server with INI overrides through the one test module. The benefit of this approach is that if you need to share the settings overrides across the tests, only one web server gets created instead of a new server for each test::

        import pytest

        from decimal import Decimal
        from _pytest.python import FixtureRequest
        from pyramid.router import Router

        import transaction

        from websauna.system.model import now
        from websauna.tests.conftest import customized_web_server


        @pytest.fixture(scope='module')
        def choose_box_web_server(request:FixtureRequest, app:Router) -> str:
            """A py.test fixture to give you a functional web server with specific INI settings overridden.

            In this case, we enable box selection screen on checkout process to test it out.
            """
            web_server_factory = customized_web_server(request, app)

            # Flip trees.choose_box settings from default test.ini value
            return web_server_factory({"trees.choose_box": True})


        def test_order_free_foxyboxy(choose_box_web_server, browser, DBSession, init):
            """Fresh user places an order and gets foxyboxy for free.."""

            web_server = choose_box_web_server

            purge_uploads(init)
            purge_redis(init)

            with transaction.manager:
                user = create_user()
                spoof_license(init, user)
                user.dispensary_membership_confirmed_at = now()

            b = browser

            b.visit("{}/cannabis-bud-box".format(web_server))

            b.find_by_css(".btn-buy-now").click()

            b.fill("email", EMAIL)
            b.find_by_name("login_email").click()
            verify_email_login(web_server, browser, init, EMAIL)

            b.find_by_css("input[value='box_foxyboxy']").click()
            b.find_by_name("next").click()

            fill_in_delivery_details(b, phone_number="+358407439707")
            confirm_delivery(b)

            assert b.is_element_present_by_css("#thank-you")


        def test_order_non_free_foxyboxy(choose_box_web_server, browser, DBSession, init):
            """Fresh user places the second order and gets foxyboxy for free.."""
            web_server = choose_box_web_server
            ...


    Inspiration: http://stackoverflow.com/a/28570677/315168

    :param app: py.test fixture for constructing a WSGI application

    :return: A factory callable you can use to spawn a web server. Pass test.ini overrides as dict to this function.
    '''

    def customized_web_server_inner(overrides:dict) -> str:

        global _customized_web_server_port

        old_settings = app.registry.settings.copy()

        app.registry.settings.update(overrides)

        host_base = HOST_BASE.replace("8521", str(_customized_web_server_port))
        _customized_web_server_port += 1

        server = ServerThread(app, host_base)
        server.start()

        # Wait randomish time to allows SocketServer to initialize itself.
        # TODO: Replace this with proper event telling the server is up.
        time.sleep(0.1)

        def teardown():
            # Restore old settings
            app.registry.settings = old_settings

            # Shutdown server thread
            server.quit()

        request.addfinalizer(teardown)
        return host_base

    return customized_web_server_inner
