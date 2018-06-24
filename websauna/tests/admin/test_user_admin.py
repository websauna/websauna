# Pyramid
import transaction

import pytest
import requests
from flaky import flaky
from splinter.driver import DriverAPI

# Websauna
from websauna.system.user.models import User
from websauna.tests.test_utils import create_logged_in_user
from websauna.tests.test_utils import create_user
from websauna.tests.test_utils import logout
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

    # b.fill("username", "test2")
    b.fill("email", "test2@example.com")
    b.fill("password", "secret")
    b.fill("password-confirm", "secret")
    b.find_by_name("add").click()

    # TODO: Convert to CSS based test
    assert b.is_element_present_by_css("#msg-item-added")

    logout(web_server, b)

    b.visit(web_server + "/login")
    b.fill("username", "test2@example.com")
    b.fill("password", "secret")
    b.find_by_name("login_email").click()

    assert b.is_element_present_by_css("#msg-you-are-logged-in")


def test_add_user_password_mismatch(browser, web_server, init, dbsession):
    """Make sure new user is not created on password mismatch."""

    b = browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    b.find_by_css("#nav-admin").click()

    b.find_by_css("#btn-panel-add-user").click()

    # b.fill("username", "test2")
    b.fill("email", "test2@example.com")
    b.fill("password", "secret")
    b.fill("password-confirm", "faied")
    b.find_by_name("add").click()

    # TODO: Convert to CSS based test
    assert b.is_text_present("Password did not match confirm")


def test_add_user_existing_email(browser, web_server, init, dbsession):
    """Add a user but there already exists one with the same email."""

    with transaction.manager:
        create_user(dbsession, init.config.registry, email="test2@example.com")

    b = browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    b.find_by_css("#nav-admin").click()

    b.find_by_css("#btn-panel-add-user").click()

    # b.fill("username", "test2")
    b.fill("email", "test2@example.com")
    b.fill("password", "secret")
    b.fill("password-confirm", "secret")
    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#error-deformField1")  # Email address already taken


def test_add_user_with_group(browser, web_server, init, dbsession):
    """Add a user and directly assign a group."""
    b = browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    b.find_by_css("#nav-admin").click()

    b.find_by_css("#btn-panel-add-user").click()

    # b.fill("username", "test2")
    b.fill("email", "test2@example.com")
    b.fill("password", "secret")
    b.fill("password-confirm", "secret")

    # TODO: Make sure checkbox widget gets proper css classes
    b.find_by_css("input[type='checkbox']")[0].click()
    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#msg-item-added")

    with transaction.manager:
        u = dbsession.query(User).get(2)
        assert len(u.groups) == 1


@flaky
def test_set_password(browser, victim_browser, web_server, init, dbsession):
    """See that we can reset the user password.

    1. Have admin user, normal user

    2. See that when the admin resets the user password all the user sessions are dropped (security feature)
    """

    b = browser
    b2 = victim_browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)
    create_logged_in_user(dbsession, init.config.registry, web_server, b2, email="victim@example.com", password="secret")

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#latest-user-shortcut").click()
    b.find_by_css("#btn-crud-set-password").click()

    b.fill("password", "new-secret")
    b.fill("password-confirm", "new-secret")
    b.find_by_name("save").click()

    assert b.is_element_present_by_css("#msg-password-changed")

    # Victim browser should have now logged out
    b2.visit(web_server)
    assert b2.is_element_present_by_css("#msg-session-invalidated")
    assert b2.is_element_present_by_css("#nav-sign-in")

    # See that we can log in with the new password
    b2.visit(web_server + "/login")
    b2.fill("username", "victim@example.com")
    b2.fill("password", "new-secret")
    b2.find_by_name("login_email").click()

    assert b2.is_element_present_by_css("#msg-you-are-logged-in")


def test_set_email(browser, victim_browser, web_server, init, dbsession):
    """Setting email resets user session and user can log in again."""

    b = browser
    b2 = victim_browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)
    create_logged_in_user(dbsession, init.config.registry, web_server, b2, email="victim@example.com", password="secret")

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#latest-user-shortcut").click()
    b.find_by_css("#btn-crud-edit").click()

    b.fill("email", "victim2@example.com")
    b.find_by_name("save").click()

    assert b.is_element_present_by_css("#msg-changes-saved")

    # Victim browser should have now logged out
    b2.visit(web_server)
    assert b2.is_element_present_by_css("#msg-session-invalidated")
    assert b2.is_element_present_by_css("#nav-sign-in")

    # See that we can log in with the new password
    b2.visit(web_server + "/login")
    b2.fill("username", "victim2@example.com")
    b2.fill("password", "secret")
    b2.find_by_name("login_email").click()

    assert b2.is_element_present_by_css("#msg-you-are-logged-in")


def test_set_enabled(browser: DriverAPI, victim_browser, web_server, init, dbsession):
    """Setting enabled resets user session. User can log after the account has been re-enabled."""
    b = browser
    b2 = victim_browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)
    create_logged_in_user(dbsession, init.config.registry, web_server, b2, email="victim@example.com", password="secret")

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#latest-user-shortcut").click()
    b.find_by_css("#btn-crud-edit").click()

    b.find_by_name("enabled").click()  # Turns off
    b.find_by_name("save").click()
    assert b.is_element_present_by_css("#msg-changes-saved")

    # Victim browser should have now logged out
    b2.visit(web_server)

    # We do not get session invalidated message this time, because request.user does not resolve for disabled user at all and middleware cannot distinct between anonymous and disabled user
    # assert b2.is_element_present_by_css("#msg-session-invalidated")
    assert b2.is_element_present_by_css("#nav-sign-in")

    # See that we cannot login on disabled user
    b2.visit(web_server + "/login")
    b2.fill("username", "victim@example.com")
    b2.fill("password", "secret")
    b2.find_by_name("login_email").click()
    assert b2.is_element_present_by_css("#msg-authentication-failure")

    # Re-enable the use
    b.find_by_css("#btn-crud-edit").click()
    b.find_by_name("enabled").click()  # Turns on
    b.find_by_name("save").click()
    assert b.is_element_present_by_css("#msg-changes-saved")

    # User can log in again

    # We get this message in wrong phase, but it's not really big deal as manual user deactivation should not be that common
    b2.visit(web_server)
    assert b2.is_element_present_by_css("#msg-session-invalidated")

    b2.visit(web_server + "/login")
    b2.fill("username", "victim@example.com")
    b2.fill("password", "secret")
    b2.find_by_name("login_email").click()
    assert b2.is_element_present_by_css("#msg-you-are-logged-in")


def test_delete_user_confirm(browser, web_server, init, dbsession):
    """Delete a user."""

    b = browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    # Create another user who we are going to delete
    with transaction.manager:
        create_user(dbsession, init.config.registry, email="foobar@example.com")

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#latest-user-shortcut").click()
    b.find_by_css("#btn-crud-delete").click()
    b.find_by_css("#btn-delete-yes").click()
    assert b.is_element_present_by_css("#msg-item-deleted")

    with transaction.manager:
        assert dbsession.query(User).count() == 1


def test_delete_user_cancel(browser, web_server, init, dbsession):
    """Delete a user, but back off on the confirmation screen."""

    b = browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    # Create another user who we are going to delete
    with transaction.manager:
        create_user(dbsession, init.config.registry, email="foobar@example.com")

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#latest-user-shortcut").click()
    b.find_by_css("#btn-crud-delete").click()
    b.find_by_css("#btn-delete-no").click()

    # Back to the show page
    assert b.is_element_present_by_css("#crud-show")

    with transaction.manager:
        assert dbsession.query(User).count() == 2


def test_csv_export_users(dbsession, registry, browser, web_server):
    """Test CSV export functionality."""

    b = browser

    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    unicode_bomb = "toholammin kevätkylvöt"

    with transaction.manager:
        u = dbsession.query(User).first()
        u.username = unicode_bomb

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-list-user").click()
    assert b.is_element_present_by_css("#btn-crud-csv-export")  # This button would trigger the download of CSV that we normally cannot test with Selenium

    # Copy session cookie over to request, so we can do an authenticated user request using requests lib
    cookies = b.driver.get_cookies()

    # Convert to plain dict
    cookies = {c["name"]: c["value"] for c in cookies}
    resp = requests.get("{}/admin/models/user/csv-export".format(web_server), cookies=cookies)

    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "text/csv; charset=utf-8"
    assert unicode_bomb in resp.text
