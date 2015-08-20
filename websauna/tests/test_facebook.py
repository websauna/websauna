import os

import transaction
import pytest

from .utils import create_user


def do_facebook_login(browser):
    """Splinter yourself in to the Facebook app."""
    b = browser

    fb_user = os.environ.get("FACEBOOK_USER")
    assert fb_user, "Please configure your Facebook secrets as environment variables to run the tests"
    fb_password = os.environ["FACEBOOK_PASSWORD"]

    assert b.is_text_present("Facebook Login")

    # FB login
    b.fill("email", fb_user)
    b.fill("pass", fb_password)
    b.find_by_css("input[name='login']").click()

    # FB allow app confirmation dialog - this is only once per user unless you reset in in your FB profile
    if b.is_text_present("will receive the following info"):
        b.find_by_css("button[name='__CONFIRM__']").click()


@pytest.mark.skipif("FACEBOOK_USER" not in os.environ, reason="Give Facebook user/pass as environment variables")
def test_facebook_first_login(web_server, browser, dbsession):
    """Login an user."""

    with transaction.manager:
        create_user()

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.find_by_css(".btn-login-facebook").click()

    do_facebook_login(browser)
    # After login we see a profile link to our profile
    # assert b.is_element_visible_by_css("#nav-logout")


@pytest.mark.skipif("FACEBOOK_USER" not in os.environ, reason="Give Facebook user/pass as environment variables")
def test_facebook_second_login(web_server, browser, dbsession):
    """Login an user."""
