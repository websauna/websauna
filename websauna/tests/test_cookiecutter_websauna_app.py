"""Test the creation of a new websauna application, using cookiecutter templates."""
# Standard Library
import os

import pytest
from flaky import flaky

from .scaffold import app_scaffold  # noQA
from .scaffold import cookiecutter_config  # noQA
from .scaffold import create_psq_db
from .scaffold import execute_venv_command
from .scaffold import replace_file
from .scaffold import start_ws_pserve


@pytest.fixture()
def dev_db(request, ini_settings):
    """Create PostgreSQL database myapcdp_dev and return its connection information."""
    dsn = ini_settings["sqlalchemy.url"]
    if dsn.startswith("sqlite://"):
        pytest.skip("These tests are run only for PostgreSQL database")
    return create_psq_db(request, "app_dev", dsn)


def test_pserve(app_scaffold, dev_db, browser):  # noQA
    """Create an application and see if ws-pserve starts. """
    # User models are needed to start the web server
    execute_venv_command("cd my.app && ws-sync-db ws://my/app/conf/development.ini", app_scaffold)
    server = start_ws_pserve("cd my.app && ws-pserve ws://my/app/conf/development.ini", app_scaffold)
    try:
        # Make sure we get some sensible output from the server
        b = browser
        b.visit("http://localhost:6543")
        # See our scaffold home page loads and demo text is there
        assert b.is_element_present_by_css("#demo-text")
    finally:
        server.kill()


# On Travis there might be abnormal delays in this test
@flaky  # noQA
def test_pyramid_debugtoolbar(app_scaffold, dev_db, browser):
    """Pyramid debug toolbar should be effective with the default development ws-pserve."""
    # User models are needed to start the web server
    execute_venv_command("ws-sync-db ws://my/app/conf/development.ini", app_scaffold, cd_folder="my.app")
    server = start_ws_pserve("cd my.app && ws-pserve ws://my/app/conf/development.ini", app_scaffold)
    try:
        # Make sure we get some sensible output from the server
        b = browser
        b.visit("http://localhost:6543/error-trigger")
        # See that Wertzkreug debugger is up
        assert b.is_element_present_by_css(".traceback")
    finally:
        server.kill()


def test_sdist(app_scaffold):  # noQA
    """Create an application and see if sdist egg can be created. """
    execute_venv_command("cd my.app && python setup.py sdist", app_scaffold)


def test_app_syncdb(app_scaffold, dev_db):  # noQA
    """Create an application and see if database is correctly created."""
    execute_venv_command("cd my.app && ws-sync-db ws://my/app/conf/development.ini", app_scaffold)


def test_shell(app_scaffold, dev_db):  # noQA
    """Create an application and see if shell is started."""
    execute_venv_command("cd my.app && ws-shell ws://my/app/conf/development.ini", app_scaffold, wait_and_see=2.0)


def test_db_shell(app_scaffold, dev_db):  # noQA
    """Create an application and see if shell is started."""
    execute_venv_command("cd my.app && ws-db-shell ws://my/app/conf/development.ini", app_scaffold, wait_and_see=2.0)


def test_gitignore(app_scaffold, dev_db):  # noQA
    """We construct a proper .gitignore file for the project."""
    assert os.path.exists(os.path.join(app_scaffold, "my.app", ".gitignore"))


def test_migration(app_scaffold, dev_db):  # noQA
    """Create an application, add a model and see if migrations are run."""
    with replace_file(os.path.join(app_scaffold, "my.app", "my", "app", "models.py"), MODELS_PY):
        # Happens if py.test picks up this test twice
        files = os.listdir(os.path.join(app_scaffold, "my.app", "alembic", "versions"))
        for f in files:
            assert not f.endswith(".py"), "versions folder contained migration scripts before initial Alembic run: {}".format(files)
        execute_venv_command("cd my.app && ws-alembic -x packages=all -c my/app/conf/development.ini revision --autogenerate -m 'Added MyModel'", app_scaffold)
        execute_venv_command("cd my.app && ws-alembic -x packages=all -c my/app/conf/development.ini upgrade head", app_scaffold)
        # Assert we got migration script for mymodel
        files = os.listdir(os.path.join(app_scaffold, "my.app", "alembic", "versions"))
        assert any("added_mymodel.py" in f for f in files), "Got files {}".format(files)


def test_app_sanity_check_fail(app_scaffold, dev_db):  # noQA
    """Create an application and see we don't start if migrations are not run."""
    execute_venv_command("cd my.app && ws-pserve ws://my/app/conf/development.ini", app_scaffold, assert_exit=1)


# DB dump on Travis might hung?
@flaky  # noQA
def test_dump_db(app_scaffold, dev_db):
    """Test database dump."""
    execute_venv_command("cd my.app && ws-sync-db ws://my/app/conf/development.ini", app_scaffold)
    execute_venv_command("cd my.app && ws-dump-db ws://my/app/conf/development.ini", app_scaffold)


# Browser doesn't come up timely on Travis
@flaky  # noQA
def test_create_user(app_scaffold, dev_db, browser):
    """Test creating user from command line and logging in as this user."""
    execute_venv_command("ws-sync-db ws://my/app/conf/development.ini", app_scaffold, cd_folder="my.app")
    exitcode, stdout, stderr = execute_venv_command("ws-create-user ws://my/app/conf/development.ini mikko@example.com secret", app_scaffold, cd_folder="my.app")
    print("Got ws-create-usr ", stdout, stderr)
    server = start_ws_pserve("cd my.app && ws-pserve ws://my/app/conf/development.ini", app_scaffold)
    try:
        # Make sure we get some sensible output from the server
        b = browser
        b.visit("http://localhost:6543/login")
        assert b.is_element_present_by_css("#login-form")
        # See our scaffold home page loads and demo text is there
        b.fill("username", "mikko@example.com")
        b.fill("password", "secret")
        b.find_by_name("login_email").click()
        assert b.is_element_present_by_css("#nav-admin")
    finally:
        server.kill()


def test_tweens(app_scaffold, dev_db):  # noQA
    """Test tweens command."""
    # TODO: Tweens should not really depent on database, but let's fix this later
    execute_venv_command("cd my.app && ws-sync-db ws://my/app/conf/development.ini", app_scaffold)
    execute_venv_command("cd my.app && ws-tweens ws://my/app/conf/development.ini", app_scaffold)


def test_create_table(app_scaffold, dev_db):  # noQA
    """Test ws-create-table command."""
    execute_venv_command("ws-create-table ws://my/app/conf/development.ini", app_scaffold, cd_folder="my.app")


def test_sanity_check(app_scaffold, dev_db):  # noQA
    """Test sanity check command."""
    execute_venv_command("ws-sanity-check ws://my/app/conf/development.ini", app_scaffold, cd_folder="my.app", assert_exit=10)
    execute_venv_command("ws-sync-db ws://my/app/conf/development.ini", app_scaffold, cd_folder="my.app")
    execute_venv_command("ws-sanity-check ws://my/app/conf/development.ini", app_scaffold, cd_folder="my.app", assert_exit=0)


#: Migration test file
MODELS_PY = """
from websauna.system.model.meta import Base
from sqlalchemy import Column
from sqlalchemy import Integer
class MyModel(Base):
    __tablename__ = "mymodel"
    id = Column(Integer, autoincrement=True, primary_key=True)
"""
