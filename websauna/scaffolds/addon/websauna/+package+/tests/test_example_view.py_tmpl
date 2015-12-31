"""An example py.test functional test case."""

import transaction

from sqlalchemy.orm.session import Session
from splinter.driver import DriverAPI

from websauna.tests.utils import create_user
from websauna.tests.utils import EMAIL
from websauna.tests.utils import PASSWORD


def test_example_view(web_server:str, browser:DriverAPI, dbsession:Session):
    """See that our example view renders correctly.

    This is a functional test. Prepare the test by creating one user in the database. Then try to login as this user by using Splinter test browser.

    :param web_server: Functional web server py.test fixture - this string points to a started web server with test.ini configuration.

    :param browser: A Splinter web browser used to execute the tests. By default ``splinter.driver.webdriver.firefox.WebDriver``, but can be altered with py.test command line options for pytest-splinter.

    :param dbsession: Active SQLAlchemy database session for the test run.
    """

    # Direct Splinter browser to the website
    b = browser
    b.visit(web_server + "/example-view")

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css("#demo-text")