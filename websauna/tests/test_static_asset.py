import shutil

import os
import pytest
from flaky import flaky
from pyramid.config import Configurator
from websauna.system import DefaultStaticAssetPolicy
from websauna.system.devop.cmdline import init_websauna
from websauna.tests.scaffold import execute_command
from websauna.tests.webserver import customized_web_server


HERE = os.path.dirname(__file__)
STATIC_CONF_FILE = os.path.join(HERE, "static-asset-test.ini")


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
    sap = DefaultStaticAssetPolicy(c)

    sap.add_static_view("websauna-static", "websauna.system:static")
    collected = sap.collect_static()

    # Check one resource from the collectin to see we succeeded
    assert collected["websauna-static"]["pyramid-32x32.png"] == 'perma-asset/pyramid-32x32.c453183eee6627ff09e49f0384cededd.png'


def test_collect_recurse():
    """Check another more complicated static file folder collect"""
    c = Configurator()
    sap = DefaultStaticAssetPolicy(c)

    sap.add_static_view("deform-static", "deform:static")
    collected = sap.collect_static()

    assert len(collected) > 0

    # Check one resource from the collectin to see we succeeded
    assert collected["deform-static"]["pickadate/translations/ja_JP.js"] == 'perma-asset/pickadate/translations/ja_JP.a773b74d6fb882ea9f8d043270e8be17.js'


@flaky
def test_map_static_asset(browser, caching_web_server):
    """Use collected information to return static URLs"""

    cache = os.path.join("websauna", "system", "static", "perma-asset")
    if os.path.exists(cache):
        shutil.rmtree(cache)

    # Run static asset collecteor
    execute_command(["ws-collect-static", STATIC_CONF_FILE], folder=os.getcwd(), timeout=30.0)

    b = browser
    b.visit(caching_web_server)

    el = b.find_by_css("link[rel='stylesheet']")[0]._element
    bootstrap_css = el.get_attribute("href")

    assert "perma-asset" in bootstrap_css
    b.visit(bootstrap_css)
    assert b.status_code.code == 200

