"""py.test fixtures for spinning up a WSGI server for functional test run."""
# Standard Library
import logging
import typing as t

# Pyramid
from pyramid.router import Router

import pytest
from webtest.http import StopableWSGIServer


logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def web_server(request, app: Router) -> str:
    """py.test fixture to create a WSGI web server for functional tests.

    The default web server address is localhost:8521. The port can be changed with ``websauna.test_web_server_port``.

    :param app: py.test fixture for constructing a WSGI application

    :return: localhost URL where the web server is running.
    """

    host = "localhost"
    port = int(app.initializer.config.registry.settings.get("websauna.test_web_server_port", 8521))

    server = StopableWSGIServer.create(app, host=host, port=port)
    server.wait()

    def teardown():
        server.shutdown()

    request.addfinalizer(teardown)
    return "http://{}:{}".format(host, port)


_customized_web_server_port = 8523


@pytest.fixture()
def customized_web_server(request, app: Router, customized_port: int=None) -> t.Callable:
    '''py.test fixture to create a WSGI web server for functional tests with custom INI options set.

    This is similar to ``web_server``, but instead directly spawning a server, it returns a factory method which you can use to launch the web server which custom parameters besides those given in test.ini.

    Example::

        def test_newsletter_splash(dbsession, customized_web_server, browser):
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
        from websauna.tests.fixtures import customized_web_server


        @pytest.fixture(scope='module')
        def choose_box_web_server(request:FixtureRequest, app:Router) -> str:
            """A py.test fixture to give you a functional web server with specific INI settings overridden.

            In this case, we enable box selection screen on checkout process to test it out.
            """
            web_server_factory = customized_web_server(request, app)

            # Flip trees.choose_box settings from default test.ini value
            return web_server_factory({"trees.choose_box": True})


        def test_order_free_foxyboxy(choose_box_web_server, browser, dbsession, init):
            """Fresh user places an order and gets foxyboxy for free.."""

            web_server = choose_box_web_server

            purge_uploads(init)
            purge_redis(init)

            with transaction.manager:
                user = create_user(dbsession)
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


        def test_order_non_free_foxyboxy(choose_box_web_server, browser, dbsession, init):
            """Fresh user places the second order and gets foxyboxy for free.."""
            web_server = choose_box_web_server
            ...


    Inspiration: http://stackoverflow.com/a/28570677/315168

    :param app: py.test fixture for constructing a WSGI application

    :param port: Force a certain port.

    :return: A factory callable you can use to spawn a web server. Pass test.ini overrides as dict to this function.
    '''

    def customized_web_server_inner(overrides: dict =None) -> str:
        global _customized_web_server_port
        old_settings = app.registry.settings.copy()
        if overrides:
            app.registry.settings.update(overrides)
        port = customized_port or _customized_web_server_port
        host_base = "http://localhost:{}".format(port)
        logger.debug("Opening a test web server at %s", host_base)
        server = StopableWSGIServer.create(app, host="localhost", port=port)
        server.wait()

        _customized_web_server_port += 1

        def teardown():
            # Restore old settings
            app.registry.settings = old_settings

            # Shutdown server thread
            server.shutdown()

        request.addfinalizer(teardown)
        return host_base

    return customized_web_server_inner
