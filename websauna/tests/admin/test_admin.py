# Standard Library
import time

# Pyramid
import transaction
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import Everyone

import pytest
from flaky import flaky

# Websauna
from websauna.system.admin.utils import get_admin
from websauna.system.user.utils import get_site_creator
from websauna.tests.test_utils import EMAIL
from websauna.tests.test_utils import PASSWORD
from websauna.tests.test_utils import create_logged_in_user
from websauna.tests.test_utils import create_user


def test_admin_permissions(test_request):
    """Non-functional test to check admin permissions are sane."""

    admin = get_admin(test_request)
    policy = test_request.registry.queryUtility(IAuthorizationPolicy)

    # Admin group access ok
    assert policy.permits(admin, "group:admin", "view")
    assert policy.permits(admin, "group:admin", "edit")
    assert policy.permits(admin, "group:admin", "delete")

    # Block world
    assert not policy.permits(admin, Everyone, "view")
    assert not policy.permits(admin, Everyone, "edit")
    assert not policy.permits(admin, Everyone, "delete")


def test_enter_admin(web_server, browser, dbsession, init):
    """The first user can open the admin page."""

    with transaction.manager:
        u = create_user(dbsession, init.config.registry)
        site_creator = get_site_creator(init.config.registry)
        site_creator.init_empty_site(dbsession, u)
        assert u.is_admin()

    b = browser
    b.visit(web_server + "/login")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    assert b.is_element_visible_by_css("#nav-admin")
    b.find_by_css("#nav-admin").click()

    assert b.is_element_present_by_css("#admin-main")


def test_non_admin_user_denied(web_server, browser, dbsession, init):
    """The second user should not see admin link nor get to the admin page."""

    with transaction.manager:
        u = create_user(dbsession, init.config.registry, admin=True)
        assert u.is_admin()

        u = create_user(dbsession, init.config.registry, email="example2@example.com")
        assert not u.is_admin()

    b = browser
    b.visit(web_server + "/login")

    b.fill("username", "example2@example.com")
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    assert not b.is_element_visible_by_css("#nav-admin")

    b.visit(web_server + "/admin/")
    assert b.is_element_visible_by_css("#forbidden")


@flaky
@pytest.mark.notebook
def test_context_sensitive_shell(web_server, browser, dbsession, init):
    """See we can open a context sensitive shell in admin."""

    b = browser
    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#latest-user-shortcut").click()
    b.find_by_css("#btn-crud-shell").click()

    # Ramping up shell takes some extended time
    time.sleep(5)

    # We succesfully exposed obj
    assert b.is_text_present("example@example.com")

    # File menu
    b.find_by_css(".dropdown a")[0].click()

    # Shutdown and Back to the home
    assert b.is_element_visible_by_css("#shutdown")
    b.find_by_css("#shutdown").click()

    # There should be alert "Do you really wish to leave notebook?"
    time.sleep(0.5)
    alert = b.driver.switch_to_alert()
    alert.accept()

    # Back to home screen
    assert b.is_element_visible_by_css("#nav-logout")
