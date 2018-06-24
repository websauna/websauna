"""Testing utility functions."""

# Standard Library
import time
import typing as t

# Pyramid
import transaction
from pyramid.interfaces import IRequest
from pyramid.registry import Registry
from pyramid.session import signed_deserialize
from zope.interface import implementer

# SQLAlchemy
from sqlalchemy.orm import Session

from pyramid_redis_sessions import RedisSession
from pyramid_redis_sessions import get_default_connection
from selenium.webdriver.remote.webdriver import WebDriver
from splinter.driver import DriverAPI

# Websauna
from websauna.system.user.interfaces import IPasswordHasher
from websauna.system.user.models import User
from websauna.system.user.utils import get_site_creator
from websauna.utils.time import now


EMAIL = "example@example.com"

#: Unit testing default password
PASSWORD = "ToholamppiMadCowz585"


def create_user(dbsession: Session, registry: Registry, email: str=EMAIL, password: str=PASSWORD, admin: bool=False) -> User:
    """A helper function to create normal and admin users for tests.

    Example:

    .. code-block:: python

        import transaction
        from websauna.tests.test_utils import create_user


        def test_some_stuff(dbsession, registry):

            with transaction.manager:
                u = create_user(registry)
                # Do stuff with new user



    :param email: User's email address. If inot given use unit testing default.

    :param password: Password as plain text. If not given use unit testing default.

    :param admin: If True run :py:class:`websauna.system.user.usermixin.SiteCreator` login and set the user to admin group.
    """

    user = User(email=email)

    if password:
        hasher = registry.getUtility(IPasswordHasher)
        user.hashed_password = hasher.hash_password(password)

    user.user_registration_source = "dummy"
    dbsession.add(user)
    dbsession.flush()
    user.username = user.generate_username()
    user.activated_at = now()

    assert user.can_login()

    # First user, make it admin
    if admin:
        site_creator = get_site_creator(registry)
        site_creator.init_empty_site(dbsession, user)

    return user


def create_logged_in_user(dbsession: Session, registry: Registry, web_server: str, browser: DriverAPI, admin: bool=False, email: str=EMAIL, password: str=PASSWORD):
    """For a web browser test session, creates a new user and log it in inside the test browser."""
    # Catch some common argument misordering issues
    assert isinstance(registry, Registry)
    assert isinstance(web_server, str)

    with transaction.manager:
        create_user(dbsession, registry, admin=admin, email=email, password=password)

    b = browser
    b.visit("{}/{}".format(web_server, "login"))

    assert b.is_element_present_by_css("#login-form")

    b.fill("username", email)
    b.fill("password", password)
    b.find_by_name("login_email").click()

    # After login we log out link to confirm login has succeeded
    assert b.is_element_present_by_css("#nav-logout")


def wait_until(callback: t.Callable, expected: object, deadline=1.0, poll_period=0.05):
    """A helper function to wait until a variable value is set (in another thread).

    This is useful for communicating between Selenium test driver and test runner main thread.

    :param callback: t.Callable which we expect to return to ``expected`` value.
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


def login(web_server: str, browser: DriverAPI, email=EMAIL, password=PASSWORD):
    """Login user to the website through the test browser."""
    b = browser
    b.visit(web_server)
    assert b.is_element_visible_by_css("#nav-sign-in"), "Could not see login button"
    b.find_by_css("#nav-sign-in").click()
    b.fill("username", email)
    b.fill("password", password)
    b.find_by_name("login_email").click()
    assert b.is_element_visible_by_css("#nav-logout")


def get_session_from_webdriver(driver: WebDriver, registry: Registry) -> RedisSession:
    """Extract session cookie from a Selenium driver and fetch a matching pyramid_redis_sesssion data.

    Example::

        def test_newsletter_referral(dbsession, web_server, browser, init):
            '''Referral is tracker for the newsletter subscription.'''

            b = browser
            b.visit(web_server + "/newsletter")

            with transaction.manager:
                r = ReferralProgram()
                r.name = "Foobar program"
                dbsession.add(r)
                dbsession.flush()
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
                assert dbsession.query(NewsletterSubscriber).count() == 1
                subscription = dbsession.query(NewsletterSubscriber).first()
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


def logout(web_server: str, browser: DriverAPI):
    """Log out the current user from the test browser."""
    browser.find_by_css("#nav-logout").click()
    assert browser.is_element_present_by_css("#msg-logged-out")


def make_dummy_request(dbsession: Session, registry: Registry) -> IRequest:
    """Creates a non-functional HTTP request with registry and dbsession configured.

    Useful for crafting requests with custom settings

    See also :func:`make_routable_request`.
    """

    @implementer(IRequest)
    class DummyRequest:
        pass

    _request = DummyRequest()
    _request.dbsession = dbsession
    _request.user = None
    _request.registry = registry

    return _request
