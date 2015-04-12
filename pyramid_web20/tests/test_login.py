import transaction

from pyramid_web20 import models

EMAIL = "example@example.com"
PASSWORD = "ToholamppiMadCowz585"


def create_user():
    user = models.User(email=EMAIL, password=PASSWORD)
    user.user_registration_source = models.User.USER_MEDIA_DUMMY
    models.DBSession.add(user)
    models.DBSession.flush()
    user.username = user.generate_username()
    assert user.can_login()
    transaction.commit()


def test_login(web_server, browser, dbsession):
    """Login an user."""

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

    create_user()

    user = models.DBSession.query(models.User).get(1)
    user.enabled = False
    assert not user.can_login()
    transaction.commit()

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
