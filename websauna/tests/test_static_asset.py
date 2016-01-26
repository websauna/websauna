import os
import pytest
from pyramid.config import Configurator
from websauna.system import DefaultStaticAssetPolicy
from websauna.system.devop.cmdline import init_websauna
from websauna.tests.scaffold import execute_command
from websauna.tests.webserver import customized_web_server


HERE = os.path.dirname(__file__)
STATIC_CONF_FILE = os.path.join(HERE, "static-asset-test.ini")


MARKER_FOLDER = "permanent-static-asset"


@pytest.fixture(scope="module")
def cache_app(request):
    """Construct a WSGI app with static asset caching enabled."""
    request = init_websauna(STATIC_CONF_FILE)
    return request.app


@pytest.fixture
def caching_web_server(request, cache_app):
    server = customized_web_server(request, cache_app)
    return server()


def test_collect_static_asset():
    """Collect static files and stash them with MD5 sums."""
    c = Configurator()
    c.registry.settings["websauna.collected_static_path"] = "/tmp/collect-static-test"
    sap = DefaultStaticAssetPolicy(c)

    sap.add_static_view("websauna-static", "websauna.system:static")
    collected = sap.collect_static()

    # Check one resource from the collectin to see we succeeded
    assert collected["websauna-static"]["pyramid-32x32.png"] == 'perma-asset/pyramid-32x32.c453183eee6627ff09e49f0384cededd.png'


def test_map_static_asset(browser, caching_web_server):
    """Use collected information to return static URLs"""

    # Run static asset collecteor
    execute_command(["ws-collect-static", STATIC_CONF_FILE], folder=os.getcwd())

    b = browser
    b.visit(caching_web_server)


def test_map_static_asset_no_collect(caching_web_server):
    """When collector has not run we cannot server static assets."""
