import transaction

from pyramid_web20.models import DBSession


def test_internal_server_error(web_server, browser):
    """When things go KABOOM show a friendly error page."""

    b = browser
    b.visit("{}/error-trigger".format(web_server))

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css("#it-is-broken")


def test_not_found(web_server, browser):
    """Show not found page on unknown URL."""


    b = browser
    b.visit("{}/foobar".format(web_server))

    assert b.is_element_visible_by_css("#not-found")


def test_forbidden(web_server, browser):
    """Access controlled page should not be available."""

    b = browser
    b.visit("{}/admin/".format(web_server))

    assert b.is_element_visible_by_css("#forbidden")
