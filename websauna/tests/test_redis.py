"""Test CSRF functionality as functional tests.

.. note ::

    These tests are leftovers from < Pyramid 1.7 when Pyramid did not have flexible CSRF protection and Websauna provided its own mechanism.

"""
import pytest

from pyramid import testing
from pyramid.httpexceptions import HTTPOk
from webtest import TestApp

from websauna.system.core.redis import get_redis


def redis_test(request):
    redis = get_redis(request)
    redis.set("foo", b"bar")
    assert redis.get("foo") == b"bar"

    redis.set("foo", "ÅÄÖ")
    assert redis.get("foo").decode("utf-8") == "ÅÄÖ"

    return HTTPOk()


@pytest.fixture()
def app(request):
    """py.test fixture to set up a dummy app for Redis testing.

    :param request: pytest's FixtureRequest (internal class, cannot be hinted on a signature)
    """

    config = testing.setUp()
    config.add_route("home", "/")
    config.add_route("redis_test", "/redis_test")
    config.add_view(redis_test, route_name="redis_test")

    def teardown():
        testing.tearDown()

    app = TestApp(config.make_wsgi_app())
    return app


def test_access_redis(app: TestApp):
    """Decorated views don't have automatic CSRF check."""

    resp = app.get("/redis_test")
    assert resp.status_code == 200
