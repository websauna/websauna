"""Test CSRF functionality as functional tests.

.. note ::

    These tests are leftovers from < Pyramid 1.7 when Pyramid did not have flexible CSRF protection and Websauna provided its own mechanism.

"""
# Pyramid
from pyramid import testing
from pyramid.exceptions import BadCSRFToken
from pyramid.testing import DummySession

import pytest
from webtest import TestApp as App

from . import csrfsamples


@pytest.fixture()
def csrf_app(request):
    """py.test fixture to set up a dummy app for CSRF testing.

    :param request: pytest's FixtureRequest (internal class, cannot be hinted on a signature)
    """

    session = DummySession()

    config = testing.setUp()
    config.set_default_csrf_options(require_csrf=True)
    config.add_route("home", "/")
    config.add_route("csrf_sample", "/csrf_sample")
    config.add_route("csrf_exempt_sample", "/csrf_exempt_sample")
    config.add_route("csrf_exempt_sample_context", "/csrf_exempt_sample_context")
    config.add_route("csrf_sample_double_argument", "/csrf_sample_double_argument/{arg}")
    config.add_route("csrf_exempt_sample_double_argument", "/csrf_exempt_sample_double_argument/{arg}")
    config.scan(csrfsamples)

    # We need sessions in order to use CSRF feature

    def dummy_session_factory(secret):
        # Return the same session over and over again
        return session

    config.set_session_factory(dummy_session_factory)

    def teardown():
        testing.tearDown()

    app = App(config.make_wsgi_app())
    # Expose session data for tests to read
    app.session = session
    return app


@pytest.fixture()
def session(request, csrf_app):
    return csrf_app.session


def test_csrf_by_default(csrf_app: App, session: DummySession):
    """CSRF goes throgh if we have a proper token."""

    resp = csrf_app.post("/csrf_sample", {"csrf_token": session.get_csrf_token()})
    assert resp.status_code == 200


def test_csrf_by_default_fail(csrf_app: App, session: DummySession):
    """CSRF error is raised by default if we try to POST to a view and we don't have token."""

    with pytest.raises(BadCSRFToken):
        csrf_app.post("/csrf_sample")


def test_csrf_exempt(csrf_app: App, session: DummySession):
    """Decorated views don't have automatic CSRF check."""

    resp = csrf_app.post("/csrf_exempt_sample")
    assert resp.status_code == 200

    resp = csrf_app.post("/csrf_exempt_sample_context")
    assert resp.status_code == 200
