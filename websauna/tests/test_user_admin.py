import transaction
from websauna.system.user.models import User

from websauna.tests.utils import create_logged_in_user
from websauna.utils.slug import uuid_to_slug


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