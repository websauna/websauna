# Pyramid
import transaction

# Websauna
from websauna.system.user.models import User
from websauna.tests.test_utils import create_logged_in_user
from websauna.tests.test_utils import create_user


def test_pagination(web_server, browser, dbsession, init):
    with transaction.manager:
        create_logged_in_user(
            dbsession,
            init.config.registry,
            web_server,
            browser,
            admin=True
        )

        for index in range(1, 101):
            u = create_user(
                dbsession,
                init.config.registry,
                email="example{}@example.com".format(index)
            )
            dbsession.add(u)

    # quick check total users
    assert dbsession.query(User).count() == 101

    b = browser
    b.visit(web_server + "/admin/models/user/listing")

    # pagination should show correct number of total
    assert b.is_text_present("Total 101 items")
    assert b.is_text_present("Page #1 (1-20 of 101)")

    # page should show 20 rows (default size)
    assert len(b.find_by_css("tr.crud-row")) == 20

    # first email should be last created
    assert b.find_by_css("td.crud-column-email").first.text == "example100@example.com"

    # pager should show 2 buttons, first 2 are disabled
    assert len(b.find_by_css(".pager li")) == 4
    assert len(b.find_by_css(".pager li.disabled")) == 2

    # click to next and repeat the above tests
    b.find_by_css(".pager li")[2].click()
    assert b.is_text_present("Total 101 items")
    assert b.is_text_present("Page #2 (21-40 of 101)")
    assert len(b.find_by_css("tr.crud-row")) == 20
    assert b.find_by_css("td.crud-column-email").first.text == "example80@example.com"
    assert len(b.find_by_css(".pager li")) == 4
    assert len(b.find_by_css(".pager li.disabled")) == 0
