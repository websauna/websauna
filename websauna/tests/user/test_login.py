# Standard Library
import ipaddress
from datetime import timedelta

# Pyramid
import deform
import transaction
from deform import Button

from webtest import TestApp as App

# Websauna
import websauna
from websauna.tests.test_utils import EMAIL
from websauna.tests.test_utils import PASSWORD
from websauna.tests.test_utils import create_user
from websauna.utils.time import now


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

    assert b.is_element_present_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    # After login we see a profile link to our profile
    assert b.is_element_present_by_css("#nav-logout")


def test_logout(web_server, browser, dbsession, init):
    """Log out."""

    with transaction.manager:
        create_user(dbsession, init.config.registry)

    b = browser
    b.visit("{}/{}".format(web_server, "login"))

    assert b.is_element_present_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    assert b.is_element_present_by_css("#msg-you-are-logged-in")
    b.find_by_css("#nav-logout").click()

    # Anonynous again
    assert b.is_element_present_by_css("#msg-logged-out")
    assert not b.is_element_present_by_css("#nav-logout")

    # We should see the log in form
    assert b.is_element_present_by_css("#login-form")


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

    assert b.is_element_present_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    assert b.is_element_present_by_css("#msg-you-are-logged-in")

    with transaction.manager:
        user = get_user(dbsession)
        assert user.last_login_ip in [ipaddress.IPv4Address("127.0.0.1"), ipaddress.IPv6Address("::1")]


def test_forget_password(web_server, browser, dbsession, init):
    """Reset password by email."""

    with transaction.manager:
        create_user(dbsession, init.config.registry)

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_present_by_css("#login-form")

    b.click_link_by_text("Forgot your password?")
    assert b.is_element_present_by_css("#forgot-password-form")
    b.fill("email", EMAIL)
    b.find_by_name("submit").click()

    assert b.is_element_present_by_css("#msg-check-email")

    with transaction.manager:
        user = get_user(dbsession)
        activation_code = user.activation.code

    b.visit("{}/reset-password/{}".format(web_server, activation_code))
    assert b.is_element_present_by_css("#reset-password-form")

    # Friendly name should be visible
    assert b.is_text_present("example@example.com")
    b.fill("password", "yyy")
    b.fill("password-confirm", "yyy")
    b.find_by_name("submit").click()

    assert b.is_element_present_by_css("#msg-password-reset-complete")

    b.fill("username", EMAIL)
    b.fill("password", "yyy")
    b.find_by_name("login_email").click()

    assert b.is_element_present_by_css("#nav-logout")


def test_forget_password_bad_user(web_server, browser, dbsession, init):
    """Reset password by email."""

    with transaction.manager:
        create_user(dbsession, init.config.registry)

    b = browser
    b.visit(web_server + "/login")

    assert b.is_element_present_by_css("#login-form")

    b.click_link_by_text("Forgot your password?")
    assert b.is_element_present_by_css("#forgot-password-form")
    b.fill("email", "foo@example.com")
    b.find_by_name("submit").click()

    assert b.is_element_present_by_css(".error-msg-detail")


def test_forget_password_disabled_user(web_server, browser, dbsession, init):
    """Reset password by email."""

    with transaction.manager:
        u = create_user(dbsession, init.config.registry)
        u.enabled = False

    b = browser
    b.visit(web_server + "/login")

    assert b.is_element_present_by_css("#login-form")

    b.click_link_by_text("Forgot your password?")
    assert b.is_element_present_by_css("#forgot-password-form")
    b.fill("email", EMAIL)
    b.find_by_name("submit").click()

    assert b.is_element_present_by_css("#msg-cannot-reset-password")


def test_bad_forget_password_activation_code(web_server, browser, dbsession):
    """Reset password by email."""
    b = browser
    b.visit("{}/reset-password/xxxx".format(web_server))

    # Check we get the pimped up not found page
    assert b.is_element_present_by_css("#not-found")


def test_login_forget_password_email_send(web_server, browser, dbsession, init):
    """Send out the reset password by email, but do not answer to it, instead directly login."""

    with transaction.manager:
        create_user(dbsession, init.config.registry)

    b = browser
    b.visit(web_server)

    b.find_by_css("#nav-sign-in").click()

    assert b.is_element_present_by_css("#login-form")

    b.click_link_by_text("Forgot your password?")
    assert b.is_element_present_by_css("#forgot-password-form")
    b.fill("email", EMAIL)
    b.find_by_name("submit").click()

    b.visit("{}/login".format(web_server))

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()
    assert b.is_element_present_by_css("#msg-you-are-logged-in")


def test_forget_password_expired_token(web_server, browser, dbsession, init):
    """Reset password by email."""

    with transaction.manager:
        create_user(dbsession, init.config.registry)

    b = browser
    b.visit(web_server + "/forgot-password")

    assert b.is_element_present_by_css("#forgot-password-form")
    b.fill("email", EMAIL)
    b.find_by_name("submit").click()

    assert b.is_element_present_by_css("#msg-check-email")

    with transaction.manager:
        user = get_user(dbsession)
        activation = user.activation
        activation.expires_at = now() - timedelta(days=365)
        activation_code = activation.code

    b.visit("{}/reset-password/{}".format(web_server, activation_code))
    assert b.is_element_present_by_css("#not-found")


def test_customize_login(paster_config):
    """Customizing login form works."""

    class CustomLoginForm(deform.Form):

        def __init__(self, *args, **kwargs):
            login_button = Button(name="login_email", title="Login by fingerprint", css_class="btn-lg btn-block")
            kwargs['buttons'] = (login_button,)
            super().__init__(*args, **kwargs)

    class Initializer(websauna.system.DemoInitializer):

        def configure_user_forms(self):

            from websauna.system.user import interfaces

            # This will set up all default forms as shown in websauna.system.Initializer.configure_user_forms
            super(Initializer, self).configure_user_forms()

            # Override the default login form with custom one
            unregister_success = self.config.registry.unregisterUtility(provided=interfaces.ILoginForm)
            assert unregister_success, "No default form register"
            self.config.registry.registerUtility(CustomLoginForm, interfaces.ILoginForm)

    global_config, app_settings = paster_config
    init = Initializer(global_config, app_settings)
    init.run()
    app = App(init.make_wsgi_app())
    resp = app.get("/login")

    assert "Login by fingerprint" in resp.text
