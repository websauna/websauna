import os

import transaction
import pytest

from .utils import create_user
from websauna.system.user.models import User


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
def test_facebook_first_login(web_server, browser, DBSession):
    """Login an user."""

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.find_by_css(".btn-login-facebook").click()

    do_facebook_login(browser)

    assert b.is_text_present("You are not logged in")

    # See that we got somewhat sane data
    with transaction.manager:
        assert DBSession.query(User).count() == 1
        u = DBSession.query(User).get(1)
        assert u.first_login
        assert u.email == os.environ["FACEBOOK_USER"]
        assert u.is_admin()  # First user becomes admin
        assert u.activated_at


@pytest.mark.skipif("FACEBOOK_USER" not in os.environ, reason="Give Facebook user/pass as environment variables")
def test_facebook_second_login(web_server, browser, DBSession):
    """Login second time through Facebook and see our first_login flag is unset.
    """
    b = browser

    # Initiate Facebook login with Authomatic
    b.visit("{}/login".format(web_server))
    b.find_by_css(".btn-login-facebook").click()

    do_facebook_login(b)
    assert b.is_text_present("You are not logged in")
    b.find_by_css("#nav-logout").click()

    # And again!
    b.visit("{}/login".format(web_server))
    b.find_by_css(".btn-login-facebook").click()
    do_facebook_login(b)

    assert b.is_text_present("You are not logged in")

    # See that we got somewhat sane data
    with transaction.manager:
        assert DBSession.query(User).count() == 1
        u = DBSession.query(User).get(1)
        assert not u.first_login
        assert u.activated_at

    b.find_by_css("#nav-logout").click()
