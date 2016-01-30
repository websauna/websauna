"""Test CSRF decorator."""
import pytest

from pyramid import testing
from pyramid.config.views import DefaultViewMapper
from pyramid.testing import DummyRequest, DummySession
from websauna.system.core.csrf import csrf_mapper_factory
from webtest import TestApp

from . import csrfsamples


@pytest.fixture(scope="module")
def csrf_app(request):
    """py.test fixture to set up a dummy app for CSRF testing.

    :param request: pytest's FixtureRequest (internal class, cannot be hinted on a signature)
    """

    request = DummyRequest()
    config = testing.setUp()
    config.set_view_mapper(csrf_mapper_factory(DefaultViewMapper))
    config.add_route("home", "/")
    config.add_route("csrf_sample", "/csrf_sample")
    config.add_route("csrf_exempt_sample", "/csrf_exempt_sample")
    config.scan(csrfsamples)

    # We need sessions in order to use CSRF feature

    def dummy_session_factory(secret):
        return DummySession()

    config.set_session_factory(dummy_session_factory)

    def teardown():
        testing.tearDown()

    app = TestApp(config.make_wsgi_app())
    return app


def test_csrf_by_default(csrf_app: TestApp):
    """CSRF error is raised by default if we try to POST to a view and we don't have token."""

    # Initialize CSRF token in session
    resp = csrf_app.get("/")

    # Sample post should go through
    resp = csrf_app.post("/csrf_sample")
    import pdb ; pdb.set_trace()


def test_csrf_exempt():
    """Test that"""



