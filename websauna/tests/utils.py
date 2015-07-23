import time
import os
from decimal import Decimal
from pyramid.registry import Registry
from pyramid.session import signed_deserialize
from pyramid_redis_sessions import RedisSession, get_default_connection
from websauna.system.model import now
from websauna.system.model import DBSession

from selenium.webdriver.remote.webdriver import WebDriver
from websauna.system.user.usermixin import check_empty_site_init

#: The default test login name
import transaction

EMAIL = "example@example.com"

#: The default test password
PASSWORD = "ToholamppiMadCowz585"


def create_user(email=EMAIL, password=PASSWORD, admin=False):
    from websauna.system.user.models import User
    from websauna.system.user.models import Group
    user = User(email=email, password=password)
    user.user_registration_source = User.USER_MEDIA_DUMMY
    DBSession.add(user)
    DBSession.flush()
    user.username = user.generate_username()

    assert user.can_login()

    # First user, make it admin
    if admin:
        check_empty_site_init(user)
        admin_grp = DBSession.query(Group).first()
        assert admin_grp
        user.groups.append(admin_grp)
        assert user.is_admin()

    return user


def get_user(email=EMAIL):
    from websauna.system.user.models import User
    return DBSession.query(User).filter_by(email=EMAIL).first()




def create_logged_in_user(web_server, browser, admin=False):
    """For a web browser test session, creates a new user and logs it in."""

    with transaction.manager:
        create_user(admin=admin)

    b = browser
    b.visit("{}/{}".format(web_server, "login"))

    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()

    # After login we log out link to confirm login has succeeded
    assert b.is_element_visible_by_css("#nav-logout")


def wait_until(callback, expected, deadline=1.0, poll_period=0.05):
    """A helper function to wait until a variable value is set (in another thread).

    :param callback: Callable which we expect to return True
    :param deadline: Seconds how long we are going to wait max
    :param poll_period: Sleep period between check attemps
    :return: The final value of callback
    """
    expires = time.time() + deadline
    while time.time() < expires:
        val = callback()
        if val == expected:
            return val
        time.sleep(poll_period)

    raise AssertionError("Callback {} did not return in expected value {} within {} seconds".format(callback, expected, deadline))


def login(web_server, browser, email=EMAIL, password=PASSWORD):
    """Login user to the website through the test browser.

    """
    b = browser
    b.visit(web_server)
    assert b.is_element_visible_by_css("#nav-sign-in"), "Could not see login button"
    b.find_by_css("#nav-sign-in").click()
    b.fill("username", email)
    b.fill("password", password)
    b.find_by_name("Log_in").click()
    assert b.is_element_visible_by_css("#nav-logout")


def get_session_from_webdriver(driver:WebDriver, registry:Registry) -> RedisSession:
    """Extract session cookie from a Selenium driver and fetch a matching pyramid_redis_sesssion data.

    Example::

        def test_newsletter_referral(DBSession, web_server, browser, init):
            '''Referral is tracker for the newsletter subscription.'''

            b = browser
            b.visit(web_server + "/newsletter")

            with transaction.manager:
                r = ReferralProgram()
                r.name = "Foobar program"
                DBSession.add(r)
                DBSession.flush()
                ref_id, slug = r.id, r.slug

            # Inject referral data to the active session. We do this because it is very hard to spoof external links pointing to localhost test web server.
            session = get_session_from_webdriver(b.driver, init.config.registry)
            session["referral"] = {
                "ref": slug,
                "referrer": "http://example.com"
            }
            session.to_redis()

            b.fill("email", "foobar@example.com")
            b.find_by_name("subscribe").click()

            # Displayed as a message after succesful form subscription
            assert b.is_text_present("Thank you!")

            # Check we get an entry
            with transaction.manager:
                assert DBSession.query(NewsletterSubscriber).count() == 1
                subscription = DBSession.query(NewsletterSubscriber).first()
                assert subscription.email == "foobar@example.com"
                assert subscription.ip == "127.0.0.1"
                assert subscription.referral_program_id == ref_id
                assert subscription.referrer == "http://example.com"

    :param driver: The active WebDriver (usually ``browser.driver``)

    :param registry: The Pyramid registry (usually ``init.config.registry``)
    """

    # Decode the session our test browser is associated with by reading the raw session cookie value and fetching the session object from Redis
    secret = registry.settings["redis.sessions.secret"]

    session_cookie = driver.get_cookie("session")["value"]
    session_id = signed_deserialize(session_cookie, secret)

    class MockRequest:
        def __init__(self, registry):
            self.registry = registry

    # Use pyramid_redis_session to get a connection to the Redis database
    redis = get_default_connection(MockRequest(registry))

    session = RedisSession(redis, session_id, new=False, new_session=None)

    return session