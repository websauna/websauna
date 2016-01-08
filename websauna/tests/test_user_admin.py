import pytest
import transaction
from websauna.system.user.models import User

from websauna.tests.utils import create_logged_in_user, create_user
from websauna.utils.slug import uuid_to_slug


@pytest.fixture
def victim_browser(request, browser_instance_getter):
    """py.test fixture to open up another web browser for password reset victim."""
    return browser_instance_getter(request, victim_browser)


def test_view_user_details(browser, web_server, init, dbsession):
    """See that we can view the details of the user in a browser."""

    b = browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    b.find_by_css("#nav-admin").click()

    b.find_by_css("#latest-user-shortcut").click()

    # TODO: Use CSS selector
    assert b.is_text_present("example@example.com")

    with transaction.manager:
        # Check that we show the user uuid slug on the page correctly
        u = dbsession.query(User).first()
        assert b.is_text_present(uuid_to_slug(u.uuid))


def test_add_user(browser, web_server, init, dbsession):
    """See that we can add new users."""

    b = browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    b.find_by_css("#nav-admin").click()

    b.find_by_css("#btn-panel-add-user").click()

    b.fill("username", "test2")
    b.fill("email", "test2@example.com")
    b.fill("password", "secret")
    b.fill("password-confirm", "secret")
    b.find_by_name("add").click()

    import pdb ; pdb.set_trace()

    # TODO: Convert to CSS based test
    assert b.is_text_present("Item added.")


def test_add_user_password_mismatch(browser, web_server, init, dbsession):
    """Make sure new user is not created on password mismatch."""

    b = browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    b.find_by_css("#nav-admin").click()

    b.find_by_css("#btn-panel-add-user").click()

    b.fill("username", "test2")
    b.fill("email", "test2@example.com")
    b.fill("password", "secret")
    b.fill("password-confirm", "faied")
    b.find_by_name("add").click()

    # TODO: Convert to CSS based test
    assert b.is_text_present("Password did not match confirm")


def test_set_password(browser, victim_browser, web_server, init, dbsession):
    """See that we can reset the user password.

    1. Have admin user, normal user

    2. See that when the admin resets the user password all the user sessions are dropped (security feature)
    """

    b = browser
    b2 = victim_browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)
    create_logged_in_user(dbsession, init.config.registry, web_server, b2, email="victim@example.com")

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#latest-user-shortcut").click()
    b.find_by_css("#btn-crud-set-password").click()

    b.fill("password", "new-secret")
    b.fill("password-confirm", "new-secret")

    # Victim browser should have now logged out
    b2.visit(web_server)
    assert b.is_element_visible_by_css("#nav-sign-in")

    # See that we can log in with the new password
    b2.visit(web_server + "/login")
    b2.fill("username", "victim@example.com")
    b2.fill("password", "new-password")
    b2.find_by_name("Log_in").click()

