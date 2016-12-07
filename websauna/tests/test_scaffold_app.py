"""Exercise websauna_app scaffold and Websauna command line scripts.

Rerunning these tests can be greatly sped up by creating a local Python package cache (wheelhouse)::

    bash websauna/tests/create_wheelhouse.bash

"""
import time
import os
import sys

import pytest
from flaky import flaky

from .scaffold import execute_venv_command
from .scaffold import replace_file
from .scaffold import app_scaffold  # noqa
from .scaffold import create_psq_db


@pytest.fixture()
def dev_db(request, ini_settings):
    """Create PostgreSQL database myapcdp_dev and return its connection information."""

    if ini_settings["sqlalchemy.url"].startswith("sqlite://"):
        pytest.skip("These tests are run only for PostgreSQL database")

    return create_psq_db(request, "myapp_dev")


@pytest.fixture()
def test_db(request, ini_settings):

    if ini_settings["sqlalchemy.url"].startswith("sqlite://"):
        pytest.skip("These tests are run only for PostgreSQL database")

    return create_psq_db(request, "myapp_test")


@pytest.mark.skipif(sys.version_info < (3,5), reason="For unknown reason this keeps randomly failing on Python 3.4")
def test_pserve(app_scaffold, dev_db, browser):
    """Create an application and see if ws-pserve starts. """

    # User models are needed to start the web server
    execute_venv_command("cd myapp && ws-sync-db myapp/conf/development.ini", app_scaffold)

    execute_venv_command("cd myapp && ws-pserve myapp/conf/development.ini --pid-file=test_pserve.pid", app_scaffold, wait_and_see=3.0)

    # Give ws-pserve some time to wake up
    time.sleep(4.0)

    try:

        # Make sure we get some sensible output from the server
        b  = browser
        b.visit("http://localhost:6543")

        # See our scaffold home page loads and demo text is there
        assert b.is_element_present_by_css("#demo-text")

    finally:
        execute_venv_command("cd myapp && ws-pserve myapp/conf/development.ini --stop-daemon --pid-file=test_pserve.pid", app_scaffold)


@flaky  # On Travis there might be abnormal delays in this test
@pytest.mark.skipif(sys.version_info < (3,5), reason="For unknown reason this keeps randomly failing on Python 3.4")
def test_pyramid_debugtoolbar(app_scaffold, dev_db, browser):
    """Pyramid debug toolbar should be effective with the default development ws-pserve."""

    # User models are needed to start the web server
    execute_venv_command("ws-sync-db myapp/conf/development.ini", app_scaffold, cd_folder="myapp")
    execute_venv_command("ws-pserve myapp/conf/development.ini --pid-file=test_pserve.pid", app_scaffold, wait_and_see=3.0, cd_folder="myapp")

    # Give ws-pserve some time to wake up in CI
    time.sleep(3.0)

    try:

        # Make sure we get some sensible output from the server
        b = browser
        b.visit("http://localhost:6543/error-trigger")

        # See that Wertzkreug debugger is up
        assert b.is_element_present_by_css(".traceback")

    finally:
        execute_venv_command("ws-pserve myapp/conf/development.ini --stop-daemon --pid-file=test_pserve.pid", app_scaffold, cd_folder="myapp")


def test_pytest(app_scaffold, test_db, scaffold_webdriver):
    """Create an application and see if py.test tests pass. """

    # Install test requirements
    execute_venv_command("cd myapp && pip install '.[test]'", app_scaffold, timeout=2*60)

    webdriver_param = scaffold_webdriver

    execute_venv_command("which py.test && py.test " + webdriver_param, app_scaffold, timeout=1*60, cd_folder="myapp")


def test_sdist(app_scaffold):
    """Create an application and see if sdist egg can be created. """
    execute_venv_command("cd myapp && python setup.py sdist", app_scaffold)


def test_app_syncdb(app_scaffold, dev_db):
    """Create an application and see if database is correctly created."""
    execute_venv_command("cd myapp && ws-sync-db myapp/conf/development.ini", app_scaffold)


def test_shell(app_scaffold, dev_db):
    """Create an application and see if shell is started."""
    execute_venv_command("cd myapp && ws-shell myapp/conf/development.ini", app_scaffold, wait_and_see=2.0)


def test_db_shell(app_scaffold, dev_db):
    """Create an application and see if shell is started."""
    execute_venv_command("cd myapp && ws-db-shell myapp/conf/development.ini", app_scaffold, wait_and_see=2.0)


def test_gitignore(app_scaffold, dev_db):
    """We construct a proper .gitignore file for the project."""
    assert os.path.exists(os.path.join(app_scaffold, "myapp", ".gitignore"))


def test_migration(app_scaffold, dev_db):
    """Create an application, add a model and see if migrations are run."""

    with replace_file(os.path.join(app_scaffold, "myapp", "myapp", "models.py"), MODELS_PY):

        # Happens if py.test picks up this test twice
        files = os.listdir(os.path.join(app_scaffold, "myapp", "alembic", "versions"))
        for f in files:
            assert not f.endswith(".py"), "versions folder contained migration scripts before initial Alembic run: {}".format(files)

        execute_venv_command("cd myapp && ws-alembic -x packages=all -c myapp/conf/development.ini revision --autogenerate -m 'Added MyModel'", app_scaffold)

        execute_venv_command("cd myapp && ws-alembic -x packages=all -c myapp/conf/development.ini upgrade head", app_scaffold)

        # Assert we got migration script for mymodel
        files = os.listdir(os.path.join(app_scaffold, "myapp", "alembic", "versions"))
        assert any("added_mymodel.py" in f for f in files), "Got files {}".format(files)


def test_app_sanity_check_fail(app_scaffold, dev_db):
    """Create an application and see we don't start if migrations are not run."""
    execute_venv_command("cd myapp && ws-pserve myapp/conf/development.ini", app_scaffold, assert_exit=1)


@flaky  # DB dump on Travis might hung?
def test_dump_db(app_scaffold, dev_db):
    """Test database dump."""
    execute_venv_command("cd myapp && ws-sync-db myapp/conf/development.ini", app_scaffold)
    execute_venv_command("cd myapp && ws-dump-db myapp/conf/development.ini", app_scaffold)


@flaky  # Browser doesn't come up timely on Travis
def test_create_user(app_scaffold, dev_db, browser):
    """Test creating user from command line and logging in as this user."""

    execute_venv_command("ws-sync-db myapp/conf/development.ini", app_scaffold, cd_folder="myapp")

    execute_venv_command("ws-create-user myapp/conf/development.ini mikko@example.com secret", app_scaffold, cd_folder="myapp")

    execute_venv_command("ws-pserve myapp/conf/development.ini --pid-file=test_pserve.pid", app_scaffold, wait_and_see=3.0, cd_folder="myapp")

    # Give ws-pserve some time to wake up in CI
    time.sleep(4)

    try:

        # Make sure we get some sensible output from the server
        b  = browser
        b.visit("http://localhost:6543/login")

        assert b.is_element_present_by_css("#login-form")

        # See our scaffold home page loads and demo text is there
        b.fill("username", "mikko@example.com")
        b.fill("password", "secret")
        b.find_by_name("login_email").click()
        assert b.is_element_present_by_css("#nav-admin")

    finally:
        execute_venv_command("cd myapp && ws-pserve myapp/conf/development.ini --stop-daemon --pid-file=test_pserve.pid", app_scaffold)


def test_tweens(app_scaffold, dev_db):
    """Test tweens command."""

    # TODO: Tweens should not really depent on database, but let's fix this later
    execute_venv_command("cd myapp && ws-sync-db myapp/conf/development.ini", app_scaffold)
    execute_venv_command("cd myapp && ws-tweens myapp/conf/development.ini", app_scaffold)


def test_create_table(app_scaffold, dev_db):
    """Test ws-create-table command."""

    execute_venv_command("ws-create-table myapp/conf/development.ini", app_scaffold, cd_folder="myapp")


def test_sanity_check(app_scaffold, dev_db):
    """Test sanity check command."""
    execute_venv_command("ws-sanity-check myapp/conf/development.ini", app_scaffold, cd_folder="myapp", assert_exit=10)
    execute_venv_command("ws-sync-db myapp/conf/development.ini", app_scaffold, cd_folder="myapp")
    execute_venv_command("ws-sanity-check myapp/conf/development.ini", app_scaffold, cd_folder="myapp", assert_exit=0)



#: Migration test file
MODELS_PY="""
from websauna.system.model.meta import Base
from sqlalchemy import Column
from sqlalchemy import Integer


class MyModel(Base):
    __tablename__ = "mymodel"
    id = Column(Integer, autoincrement=True, primary_key=True)

"""