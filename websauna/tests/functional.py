"""Functional testing with WSGI server."""


import threading
import time
from wsgiref.simple_server import make_server
from urllib.parse import urlparse
from pyramid.paster import bootstrap

import pytest
from webtest import TestApp

from backports import typing

#: The URL where WSGI server is run from where Selenium browser loads the pages
HOST_BASE = "http://localhost:8521"

PAGE_LOAD_TIMEOUT = 3


class ServerThread(threading.Thread):
    """ Run WSGI server on a background thread.

    Pass in WSGI app object and serve pages from it for Selenium browser.
    """

    def __init__(self, app, hostbase=HOST_BASE):
        threading.Thread.__init__(self)
        self.app = app
        self.srv = None
        self.daemon = True
        self.hostbase = hostbase

    def run(self):
        """
        Open WSGI server to listen to HOST_BASE address
        """
        parts = urlparse(self.hostbase)
        domain, port = parts.netloc.split(":")
        self.srv = make_server(domain, int(port), self.app)
        try:
            self.srv.serve_forever()
        except Exception as e:
            # We are a background thread so we have problems to interrupt tests in the case of error
            import traceback
            traceback.print_exc()
            # Failed to start
            self.srv = None

    def quit(self):
        """Stop test webserver."""
        if self.srv:
            self.srv.shutdown()


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

    assert server.srv is not None, "Could not start the test web server"

    host_base = HOST_BASE

    def teardown():
        server.quit()

    request.addfinalizer(teardown)
    return host_base



_customized_web_server_port = 8522

@pytest.fixture()
def customized_web_server(request, app) -> typing.Callable:
    """py.test fixture to create a WSGI web server for functional tests with custom INI options set.

    This is similar to ``web_server``, but instead directly spawning a server, it returns a factory method which you can use to launch the web server which custom parameters besides those given in test.ini.

    Example::

        def test_newsletter_splash(DBSession, customized_web_server, browser):
            '''All visitors get a newsletter subscription dialog when arriving to the landing page.

            :param dbsession: py.test fixture for
            :param ini_settings: py.test fixture for loading INI settings from command line
            '''

            # Create a WSGI server where newsletter splash dialog is explicitly enabled (disabled by default for testing)
            web_server = customized_web_server({"trees.newsletter_splash": True})

            b = browser
            b.visit(web_server)

            # Scroll down a bit to trigger the dialog
            browser.driver.execute_script("window.scrollTo(0, 10)")

            # Wait the dialog to come up
            time.sleep(2)


    Inspiration: http://stackoverflow.com/a/28570677/315168

    :param app: py.test fixture for constructing a WSGI application

    :return: A factory function you can use to spawn a web server. Optional kwargs dict can be passed to this function.
    """

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

        assert server.srv is not None, "Could not start the test web server at {}".format(host_base)

        def teardown():
            # Restore old settings
            app.settings = old_settings

            # Shutdown server thread
            server.quit()

        request.addfinalizer(teardown)
        return host_base

    return customized_web_server_inner



@pytest.fixture(scope='session')
def light_web_server(request, app):
    """Creates a test web server which does not give any CSS and JS assets to load.

    Because the server life-cycle is one test session and we run with different settings we need to run a in different port.

    TODO: Remove - make this configuration for web_server()
    """

    app.initializer.config.registry["websauna.testing_skip_css"] = True
    app.initializer.config.registry["websauna.testing_skip_js"] = True

    host_base = "http://localhost:8522"

    server = ServerThread(app, host_base)
    server.start()

    # Wait randomish time to allows SocketServer to initialize itself.
    # TODO: Replace this with proper event telling the server is up.
    time.sleep(0.1)

    assert server.srv is not None, "Could not start the test web server"

    app = TestApp(app)

    def teardown():
        server.quit()

    request.addfinalizer(teardown)
    return host_base
