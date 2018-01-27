"""Localhost tunneling utilities for running callback tests against external services."""

# Standard Library
import logging
import subprocess
import tempfile
import time
from distutils.spawn import find_executable


logger = logging.getLogger(__name__)


class NgrokTunnel:
    """Build a tunnel to the test webserver using Ngrok service, exposing the test server to the world.

    When you are testing against third party services which call back your site, you need to make sure the test web server can get called. Usually the third party sites allow configuration of fixed callback locations only. Thus, for the testing, on the third party site, we define a fixed callback pointing to ngrok.io location. Then we use ngrok API to route this location to our test webserver at the beginning of the test run.

    Example::

        @pytest.fixture(scope='module')
        def ngrok_tunnel(request:FixtureRequest, ini_settings:dict, web_server:str) -> NgrokTunnel:
            '''A py.test fixture to build tunnel to test SericaPay payment callbacks.

            The SericaPay has a preconfigured test account with a callback pointing to a Ngrok tunnel entry point. When the functional test suite runs SericaPay tests, it builds the tunnel localhost<->ngrok endpoint at the beginning of the test module executing.
            '''

            # Where is our test web server running
            port = urlparse(web_server).port

            # Construct Ngrok tunnel wrapper
            tunnel = NgrokTunnel(port, ini_settings["trees.ngrok_auth_token"], subdomain="trees")

            request.addfinalizer(tunnel.stop)

            tunnel.start()

            return tunnel


        @pytest.mark.serica
        def test_serica_payment(web_server, browser, dbsession, init, ngrok_tunnel):
            '''Do a Serica payment and see it works.'''

    """

    def __init__(self, port: int, auth_token: str, subdomain: str):
        """Build ngrok HTTP tunnel

        Assume ngrok version 2.x. A temporary ngrok configuration file is created where the ngrok token is stored for running the command.

        :param port: localhost port forwarded through tunnel

        :param auth_token: Ngrok auth token to use

        :param subdomain: Use this subdomain for the tunnelling
        """
        assert find_executable("ngrok"), "ngrok command must be installed, see https://ngrok.com/"
        self.port = port
        self.auth_token = auth_token
        self.subdomain = subdomain
        self.ngrok = None
        self.config_file_handle, self.config_file = tempfile.mkstemp()

    def start(self, ngrok_die_check_delay=2.0):
        """Starts the thread on the background and blocks until we get a tunnel URL.

        :param ngrok_die_check_delay: Enough to get the error from ngrok service "Your account is limited to one tunnel"

        :return: the tunnel URL which is now publicly open for your localhost port
        """

        logger.debug("Starting ngrok tunnel %s for port %d", self.subdomain, self.port)

        try:
            subprocess.check_output(["ngrok", "authtoken", self.auth_token, "--config", self.config_file])
        except subprocess.CalledProcessError as e:
            raise AssertionError("Configuring ngrok failed: {}".format(e.output)) from e

        # TODO: capture ngrok output in the case of an error.... no actual ngrok failure reason is not printed
        self.ngrok = subprocess.Popen(["ngrok", "http", str(self.port), "--subdomain", self.subdomain, "--config", self.config_file], stdout=subprocess.DEVNULL)

        # See that we don't instantly die, wait ngrok API to throw us an error
        time.sleep(ngrok_die_check_delay)
        assert self.ngrok.poll() is None, "ngrok terminated abrutly"
        url = "https://{}.ngrok.com".format(self.subdomain)
        return url

    def stop(self):
        """Tell ngrok to tear down the tunnel.

        Stop the background tunneling process.
        """
        if self.ngrok and self.ngrok.returncode is None:
            self.ngrok.terminate()
