"""Test view permission as functional tests."""
# Pyramid
import transaction

# SQLAlchemy
from sqlalchemy.orm import Session

import pytest

# Websauna
import websauna
from websauna.tests.test_utils import create_user
from websauna.tests.test_utils import login
from websauna.tests.webserver import customized_web_server

from . import permissionsamples


@pytest.fixture(scope="module")
def permission_app(request, paster_config):
    '''Custom WSGI app with permission test views enabled.'''

    class Initializer(websauna.system.DemoInitializer):

        def configure_views(self):
            super(Initializer, self).configure_views()
            self.config.scan(permissionsamples)

        def configure_csrf(self):
            """Disable CSRF for this test run for making testing simpler."""
            self.config.set_default_csrf_options(require_csrf=False)

    global_config, app_settings = paster_config
    init = Initializer(global_config, app_settings)
    init.run()
    app = init.make_wsgi_app()
    app.init = init
    return app


@pytest.fixture(scope="module")
def web_server(request, permission_app):
    """Run a web server with custom permission test views enabled."""

    web_server_factory = customized_web_server(request, permission_app)
    _web_server = web_server_factory()
    return _web_server


def test_autheticated_anonymous_not_allowed(web_server, dbsession: Session, init, browser):
    """Anonymous access is not allowed to the views protected by authenticate permission."""
    b = browser
    b.visit("{}/test_authenticated".format(web_server))
    assert b.is_element_present_by_css("#forbidden")


def test_logged_in_has_authenticated_permission(web_server, dbsession: Session, browser, permission_app):
    """Logged in users can access views behind authenticated permission."""

    b = browser

    with transaction.manager:
        create_user(dbsession, permission_app.init.config.registry)

    b.visit(web_server)
    login(web_server, b)

    # Logged in user can access
    b.visit("{}/test_authenticated".format(web_server))
    assert b.is_element_present_by_css("#ok")
