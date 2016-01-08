import transaction
from websauna.tests.utils import create_user
from websauna.tests.utils import EMAIL
from websauna.tests.utils import PASSWORD


def get_user(dbsession):
    from websauna.system.user.models import User
    return dbsession.query(User).get(1)


def test_login(web_server, browser, dbsession, init):
    """Login an user."""

    with transaction.manager:
        create_user(dbsession, init.config.registry)

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css("#nav-logout")


def test_login_inactive(web_server, browser, dbsession, init):
    """Login disabled user account."""

    with transaction.manager:
        create_user(dbsession, init.config.registry)

    with transaction.manager:
        user = get_user(dbsession)
        user.enabled = False
        assert not user.can_login()

    b = browser
    b.visit("{}/{}".format(web_server, "login"))

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    # After login we see a profile link to our profile
    assert not b.is_element_visible_by_css("#nav-logout")

    assert b.is_text_present("Account log in disabled.")


def test_logout(web_server, browser, dbsession, init):
    """Log out."""

    with transaction.manager:
        create_user(dbsession, init.config.registry)

    b = browser
    b.visit("{}/{}".format(web_server, "login"))

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    b.find_by_css("#nav-logout").click()

    # Anonynous again
    assert not b.is_element_visible_by_css("#nav-logout")

    # We should see the log in form
    assert b.is_element_visible_by_css("#login-form")


def test_last_login_ip(web_server, browser, dbsession, init):
    """Record last log in IP correctly."""

    with transaction.manager:
        create_user(dbsession, init.config.registry)

    with transaction.manager:
        user = get_user(dbsession)
        assert not user.last_login_ip

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    with transaction.manager:
        user = get_user(dbsession)
        assert user.last_login_ip == "127.0.0.1"


def test_forget_password(web_server, browser, dbsession, init):
    """Reset password by email."""

    with transaction.manager:
        user = create_user(dbsession, init.config.registry)

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.click_link_by_text("Forgot your password?")
    assert b.is_element_visible_by_css("#forgot-password-form")
    b.fill("email", EMAIL)
    b.find_by_name("submit").click()

    assert b.is_text_present("Please check your email")

    with transaction.manager:
        user = get_user(dbsession)
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
    b.find_by_name("login_email").click()

    assert b.is_element_visible_by_css("#nav-logout")


def test_bad_forget_password_activation_code(web_server, browser, dbsession):
    """Reset password by email."""
    b = browser
    b.visit("{}/reset-password/xxxx".format(web_server))

    # Check we get the pimped up not found page
    assert b.is_element_visible_by_css("#not-found")
