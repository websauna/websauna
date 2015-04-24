import transaction

from pyramid_web20.models import DBSession

from pyramid_web20.tests.utils import create_user
from pyramid_web20.tests.utils import EMAIL
from pyramid_web20.tests.utils import PASSWORD



def get_user():
    from pyramid_web20.system.user.models import User
    from pyramid_web20 import models
    return models.DBSession.query(User).get(1)


def test_login(web_server, browser, dbsession):
    """Login an user."""

    with transaction.manager:
        create_user()

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css("#nav-logout")


def test_login_inactive(web_server, browser, dbsession):
    """Login disabled user account."""

    with transaction.manager:
        create_user()

    with transaction.manager:
        user = get_user()
        user.enabled = False
        assert not user.can_login()

    b = browser
    b.visit("{}/{}".format(web_server, "login"))

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()

    # After login we see a profile link to our profile
    assert not b.is_element_visible_by_css("#nav-logout")

    assert b.is_text_present("Account log in disabled.")


def test_logout(web_server, browser, dbsession):
    """Log out."""

    with transaction.manager:
        create_user()

    b = browser
    b.visit("{}/{}".format(web_server, "login"))

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()

    b.find_by_css("#nav-logout").click()

    # Anonynous again
    assert not b.is_element_visible_by_css("#nav-logout")

    # We should see the log in form
    assert b.is_element_visible_by_css("#login-form")


def test_last_login_ip(web_server, browser, dbsession):
    """Record last log in IP correctly."""

    with transaction.manager:
        create_user()

    with transaction.manager:
        user = get_user()
        assert not user.last_login_ip

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()

    with transaction.manager:
        user = get_user()
        assert user.last_login_ip == "127.0.0.1"



def test_forget_password(web_server, browser, dbsession):
    """Reset password by email."""

    with transaction.manager:
        user = create_user()

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.click_link_by_text("Forgot your password?")
    assert b.is_element_visible_by_css("#forgot-password-form")
    b.fill("email", EMAIL)
    b.find_by_name("submit").click()

    assert b.is_text_present("Please check your e-mail")

    with transaction.manager:
        user = get_user()
        activation_code = user.activation.code

    b.visit("{}/reset-password/{}".format(web_server, activation_code))
    assert b.is_element_visible_by_css("#reset-password-form")

    # Friendly name should be visible
    assert b.is_text_present("example@example.com")
    b.fill("password", "yyy")
    b.fill("password-confirm", "yyy")
    b.find_by_name("submit").click()

    assert b.is_text_present("The password reset complete.")

    b.fill("username", EMAIL)
    b.fill("password", "yyy")
    b.find_by_name("Log_in").click()

    assert b.is_element_visible_by_css("#nav-logout")


def test_bad_forget_password_activation_code(web_server, browser, dbsession):
    """Reset password by email."""
    b = browser
    b.visit("{}/reset-password/xxxx".format(web_server))

    # Check we get the pimped up not found page
    assert b.is_element_visible_by_css("#not-found")
