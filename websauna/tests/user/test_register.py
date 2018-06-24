# Standard Library
from datetime import timedelta

# Pyramid
import transaction

# Websauna
from websauna.system.user.models import Activation
from websauna.system.user.models import User
from websauna.utils.time import now


EMAIL = "example@example.com"
PASSWORD = "ToholamppiMadCowz585"


def get_user(dbsession):
    from websauna.system.user.models import User
    return dbsession.query(User).get(1)


def test_register_email(web_server, browser, dbsession):
    """Register on the site and login after activation."""

    b = browser
    b.visit(web_server)

    b.find_by_css("#nav-sign-up").click()

    assert b.is_element_present_by_css("#sign-up-form")

    b.fill("email", EMAIL)
    b.fill("password", PASSWORD)
    b.fill("password-confirm", PASSWORD)

    b.find_by_name("sign_up").click()

    assert b.is_element_present_by_css("#waiting-for-activation")

    # Now peek the Activation link from the database
    user = get_user(dbsession)
    assert user.activation.code

    activation_link = "{}/activate/{}".format(web_server, user.activation.code)

    b.visit(activation_link)

    assert b.is_element_present_by_css("#sign-up-complete")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    # After login we see a profile link to our profile
    assert b.is_element_present_by_css("#nav-logout")


def test_register_email_activation_expired(web_server, browser, dbsession):
    """Register on the site, let the first activation expire, register through reset password."""

    b = browser

    b.visit(web_server + "/register")
    assert b.is_element_visible_by_css("#sign-up-form")

    b.fill("email", EMAIL)
    b.fill("password", PASSWORD)
    b.fill("password-confirm", PASSWORD)

    b.find_by_name("sign_up").click()

    assert b.is_element_visible_by_css("#waiting-for-activation")

    with transaction.manager:
        a = dbsession.query(Activation).get(1)
        u = dbsession.query(User).get(1)  # noQA
        a.expires_at = now() - timedelta(days=365)
        activation_code = a.code

    activation_link = "{}/activate/{}".format(web_server, activation_code)
    b.visit(activation_link)

    assert b.is_element_present_by_css("#not-found")

    b.visit(web_server + "/login")
    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    # Cannot login because activation expired
    assert b.is_element_present_by_css("#msg-authentication-failure")

    # Reset password
    b.visit(web_server + "/forgot-password")
    assert b.is_element_present_by_css("#forgot-password-form")
    b.fill("email", EMAIL)
    b.find_by_name("submit").click()

    assert b.is_element_present_by_css("#msg-check-email")

    with transaction.manager:
        user = get_user(dbsession)
        activation = user.activation
        activation_code = activation.code

    b.visit("{}/reset-password/{}".format(web_server, activation_code))

    b.fill("password", "yyy")
    b.fill("password-confirm", "yyy")
    b.find_by_name("submit").click()

    assert b.is_element_present_by_css("#msg-password-reset-complete")

    b.fill("username", EMAIL)
    b.fill("password", "yyy")
    b.find_by_name("login_email").click()

    assert b.is_element_present_by_css("#msg-you-are-logged-in")
