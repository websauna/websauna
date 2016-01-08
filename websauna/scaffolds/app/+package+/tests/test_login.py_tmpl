"""An example login test case."""

import transaction

from sqlalchemy.orm.session import Session
from splinter.driver import DriverAPI

from websauna.tests.utils import create_user
from websauna.tests.utils import EMAIL
from websauna.tests.utils import PASSWORD
from websauna.system import Initializer


def test_login(web_server:str, browser:DriverAPI, dbsession:Session, init:Initializer):
    """Login as a user to the site.

    This is a functional test. Prepare the test by creating one user in the database. Then try to login as this user by using Splinter test browser.

    :param web_server: Functional web server py.test fixture - this string points to a started web server with test.ini configuration.

    :param browser: A Splinter web browser used to execute the tests. By default ``splinter.driver.webdriver.firefox.WebDriver``, but can be altered with py.test command line options for pytest-splinter.

    :param dbsession: Active SQLAlchemy database session for the test run.

    :param init: Websauna Initializer which ramps up the environment with the default ``test.ini`` and exposes the test config.
    """

    with transaction.manager:
        # Create a dummy example@example.com user we test
        create_user(dbsession, init.config.registry, email=EMAIL, password=PASSWORD)

    # Direct Splinter browser to the website
    b = browser
    b.visit(web_server)

    # This link should be in the top navigation
    b.find_by_css("#nav-sign-in").click()

    # Link gives us the login form
    assert b.is_element_visible_by_css("#login-form")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("login_email").click()

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css("#nav-logout")