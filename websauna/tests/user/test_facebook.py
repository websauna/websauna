"""Facebook login tests.

To run::

    FACEBOOK_USER="x@example.com" FACEBOOK_PASSWORD="y" py.test websauna -s --splinter-webdriver=firefox --splinter-make-screenshot-on-failure=false --ini=test.ini -k test_facebook


"""
# Standard Library
import os

# Pyramid
import transaction

import pytest
from flaky import flaky

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.user.models import User
from websauna.tests.test_utils import create_user
from websauna.tests.webserver import customized_web_server


HERE = os.path.dirname(__file__)

#: Selector we use to detect if we are on the Facebook login page
FACEBOOK_LOGIN_TEST_CSS = "#pageFooter"


@pytest.fixture(scope="module")
def facebook_app(request):
    """Construct a WSGI app with tutorial models and admins loaded."""
    ini_file = os.path.join(HERE, "facebook-test.ini")
    request = init_websauna(ini_file)
    return request.app


_web_server = None


@pytest.fixture(scope="module")
def web_server(request, facebook_app):
    """Run a web server with Facebook login settings."""

    # We cache the web server here, so that @flaky doesn't try to recreate it in the same port
    # when Zuckerberg's high quality product fails
    global _web_server

    # customized_port must match one in Facebook app settings
    if not _web_server:
        web_server_factory = customized_web_server(request, facebook_app, customized_port=6662)
        _web_server = web_server_factory()

    return _web_server


def do_facebook_login(browser):
    """Splinter yourself in to the Facebook app."""
    b = browser

    fb_user = os.environ.get("FACEBOOK_USER")
    assert fb_user, "Please configure your Facebook secrets as environment variables to run the tests"
    fb_password = os.environ["FACEBOOK_PASSWORD"]

    assert browser.is_element_present_by_css(FACEBOOK_LOGIN_TEST_CSS)

    # FB login
    b.fill("email", fb_user)
    b.fill("pass", fb_password)
    b.find_by_css("button[name='login']").click()

    # FB allow app confirmation dialog - this is only once per user unless you reset in in your FB profile
    if b.is_text_present("will receive the following info"):
        b.find_by_css("button[name='__CONFIRM__']").click()

    assert b.is_element_present_by_css("#msg-you-are-logged-in")


def do_facebook_login_if_facebook_didnt_log_us_already(browser):
    """Facebook doesn't give us login dialog again as the time is so short, or Authomatic does some caching here?."""

    if browser.is_element_present_by_css(FACEBOOK_LOGIN_TEST_CSS):
        do_facebook_login(browser)
    else:
        # Clicking btn-facebook-login goes directly through to the our login view
        pass


@pytest.mark.skipif(not os.environ.get("FACEBOOK_USER"), reason="Give Facebook user/pass as environment variables")
@flaky
def test_facebook_first_login(web_server, browser, dbsession):
    """Login an user."""

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.find_by_css(".btn-login-facebook").click()
    do_facebook_login_if_facebook_didnt_log_us_already(browser)
    assert b.is_element_present_by_css("#msg-you-are-logged-in")

    # See that we got somewhat sane data
    with transaction.manager:
        assert dbsession.query(User).count() == 1
        u = dbsession.query(User).get(1)
        assert u.first_login
        assert u.email == os.environ["FACEBOOK_USER"]
        assert u.is_admin()  # First user becomes admin
        assert u.activated_at

    b.find_by_css("#nav-logout").click()


@pytest.mark.skipif(not os.environ.get("FACEBOOK_USER"), reason="Give Facebook user/pass as environment variables")
@flaky
def test_facebook_second_login(web_server, browser, dbsession):
    """Login second time through Facebook and see our first_login flag is unset.
    """
    b = browser

    # Initiate Facebook login with Authomatic
    b.visit("{}/login".format(web_server))
    b.find_by_css(".btn-login-facebook").click()

    do_facebook_login_if_facebook_didnt_log_us_already(b)
    assert b.is_text_present("You are now logged in")
    b.find_by_css("#nav-logout").click()

    assert b.is_element_present_by_css("#msg-logged-out")

    # And again!

    b.visit("{}/login".format(web_server))
    b.find_by_css(".btn-login-facebook").click()

    do_facebook_login_if_facebook_didnt_log_us_already(b)

    assert b.is_element_present_by_css("#msg-you-are-logged-in")

    # See that we got somewhat sane data
    with transaction.manager:
        assert dbsession.query(User).count() == 1
        u = dbsession.query(User).get(1)
        assert not u.first_login
        assert u.activated_at

    b.find_by_css("#nav-logout").click()


@pytest.mark.skipif(not os.environ.get("FACEBOOK_USER"), reason="Give Facebook user/pass as environment variables")
@flaky
def test_facebook_login_disabled_user(web_server, browser, dbsession, init):
    """Logged in user which is not enabled should give an error.."""

    with transaction.manager:
        u = create_user(dbsession, init.config.registry, email=os.environ["FACEBOOK_USER"])
        u.enabled = False

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.find_by_css(".btn-login-facebook").click()

    do_facebook_login_if_facebook_didnt_log_us_already(browser)

    assert b.is_element_present_by_css("#msg-cannot-login-social-media-user")
