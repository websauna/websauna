"""Test view throttlign facilities."""
# Pyramid
from pyramid.httpexceptions import HTTPOk

import pytest
from webtest import TestApp as App

# Websauna
import websauna
from websauna.system.core.redis import get_redis  # noQA
from websauna.system.form.throttle import clear_throttle
from websauna.system.form.throttle import throttled_view


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
    app = App(init.make_wsgi_app())
    app.init = init
    return app


def test_throttle(throttle_app: App, test_request):
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
