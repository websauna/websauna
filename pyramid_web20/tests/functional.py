"""Functional testing with WSGI server."""


import threading
import time
from wsgiref.simple_server import make_server
from urllib.parse import urlparse

import pytest
from webtest import TestApp

from pyramid_web20 import get_init

#: The URL where WSGI server is run from where Selenium browser loads the pages
HOST_BASE = "http://localhost:8521"

PAGE_LOAD_TIMEOUT = 3


class ServerThread(threading.Thread):
    """ Run WSGI server on a background thread.

    Pass in WSGI app object and serve pages from it for Selenium browser.
    """

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.srv = None
        self.daemon = True

    def run(self):
        """
        Open WSGI server to listen to HOST_BASE address
        """
        parts = urlparse(HOST_BASE)
        domain, port = parts.netloc.split(":")
        self.srv = make_server(domain, int(port), self.app)
        try:
            self.srv.serve_forever()
        except:
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
def web_server(request, ini_settings):
    """Have a WSGI server for running functional tests."""

    init = get_init(ini_settings)
    init.run(ini_settings)
    app = init.make_wsgi_app()

    server = ServerThread(app)
    server.start()

    # Wait randomish time to allows SocketServer to initialize itself.
    # TODO: Replace this with proper event telling the server is up.
    time.sleep(0.1)

    assert server.srv is not None, "Could not start the test web server"

    app = TestApp(app)

    host_base = HOST_BASE

    def teardown():
        server.quit()

    request.addfinalizer(teardown)
    return host_base
