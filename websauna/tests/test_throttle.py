"""Test view throttlign facilities."""
import pytest
from pyramid import testing

import websauna
from pyramid.httpexceptions import HTTPOk, HTTPTooManyRequests
from pyramid.registry import Registry
from pyramid.view import view_config
from websauna.system.core.redis import get_redis
from websauna.system.form.throttle import throttled_view, clear_throttle
from webtest import TestApp


def throttle_sample(request):
    return HTTPOk()


@pytest.fixture(scope="module")
def throttle_app(request, paster_config):
    '''Custom WSGI app with permission test views enabled.'''

    class Initializer(websauna.system.Initializer):

        def configure_views(self):
            self.config.add_route("throttle_sample", "/")
            self.config.add_view(throttle_sample, route_name="throttle_sample", decorator=throttled_view(limit=1))

        def configure_csrf(self):
            """Disable CSRF for this test run for making testing simpler."""
            self.config.set_default_csrf_options(require_csrf=False)

    global_config, app_settings = paster_config
    init = Initializer(global_config, app_settings)
    init.run()
    app = TestApp(init.make_wsgi_app())
    app.init = init
    return app


def test_throttle(throttle_app: TestApp, test_request):
    """Throttling should give us 429."""

    app = throttle_app

    # clear counter from previous test run
    clear_throttle(test_request, "throttle_sample")

    app.get("/", status=200)

    # We exceeded the limit of 1 request per hour
    app.get("/", status=429)

    # Let's clear the counter
    clear_throttle(test_request, "throttle_sample")

    app.get("/", status=200)
