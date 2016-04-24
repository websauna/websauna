import time

import transaction
from flaky import flaky

from websauna.system.user.utils import get_site_creator
from websauna.tests.utils import create_user, EMAIL, PASSWORD, create_logged_in_user


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

    assert b.is_element_visible_by_css("#admin-main")


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

    b.find_by_css("#pyramid_notebook_shutdown").click()

    # Back to home screen
    assert b.is_element_visible_by_css("#nav-logout")
