import transaction

from websauna.tests.utils import create_user, create_logged_in_user


def test_view_user_details(browser, web_server, init, dbsession):
    """See that we can view the details of the user in a browser."""

    b = browser

    create_logged_in_user(dbsession, init.config.registry, web_server, browser, admin=True)

    b.find_by_css("#nav-admin").click()

    b.find_by_css("#latest-user-shortcut").click()

    # TODO: Use CSS selector
    assert b.is_text_present("example@example.com")