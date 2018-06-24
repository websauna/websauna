# Standard Library
import os

import pytest

# Websauna
from websauna.system import Initializer
from websauna.system.core.route import add_template_only_view
from websauna.tests.fixtures import get_app
from websauna.tests.webserver import customized_web_server


HERE = os.path.abspath(os.path.dirname(__file__))


def extra_init(init: Initializer):
    """Configure one templated only view."""
    config = init.config
    config.add_jinja2_search_path(HERE + "/templates", name=".html")
    add_template_only_view(config, "/dummy", "dummy", "dummy.html")


@pytest.fixture(scope="module")
def app(request, ini_settings):
    """Construct a WSGI app with tutorial models and admins loaded."""
    app = get_app(ini_settings, extra_init=extra_init)
    return app


@pytest.fixture(scope="module")
def web_server(request, app):
    """Run a web server
    with tutorial installed."""
    web_server = customized_web_server(request, app)
    return web_server()


def test_template_only_view(browser, web_server):
    """See that we can register and render a template only view."""

    browser.visit(web_server + "/dummy")
