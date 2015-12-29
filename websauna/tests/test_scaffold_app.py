"""Exercise websauna_app scaffold and Websauna command line scripts.

Rerunning these tests can be greatly sped up by creating a local Python package cache (wheelhouse)::

    bash websauna/tests/create_wheelhouse.bash

"""
import os
import pytest

from .scaffold import execute_venv_command
from .scaffold import replace_file
from .scaffold import app_scaffold  # noqa
from .scaffold import create_psq_db


@pytest.fixture()
def dev_db(request):
    """Create PostgreSQL database myapcdp_dev and return its connection information."""
    return create_psq_db(request, "myapp_dev")


@pytest.fixture()
def test_db(request):
    return create_psq_db(request, "myapp_test")


def test_pserve(app_scaffold, dev_db, browser):
    """Create an application and see if pserve starts. """

    # User models are needed to start the web server
    execute_venv_command("cd myapp && ws-sync-db development.ini", app_scaffold)

    execute_venv_command("cd myapp && pserve development.ini --pid-file=test_pserve.pid", app_scaffold, wait_and_see=3.0)

    try:

        # Make sure we get some sensible output from the server
        b  = browser
        b.visit("http://localhost:6543")

        # See our scaffold home page loads and demo text is there
        assert b.is_element_present_by_css("#demo-text")

    finally:
        execute_venv_command("cd myapp && pserve development.ini --stop-daemon --pid-file=test_pserve.pid", app_scaffold)


def test_pyramid_debugtoolbar(app_scaffold, dev_db, browser):
    """Pyramid debug toolbar should be effective with the default development pserve."""

    # User models are needed to start the web server
    execute_venv_command("ws-sync-db development.ini", app_scaffold, cd_folder="myapp")
    execute_venv_command("pserve development.ini --pid-file=test_pserve.pid", app_scaffold, wait_and_see=3.0, cd_folder="myapp")

    try:

        # Make sure we get some sensible output from the server
        b  = browser
        b.visit("http://localhost:6543/error-trigger")

        # See that Wertzkreug debugger is up
        assert b.is_element_present_by_css(".errormsg")

    finally:
        execute_venv_command("pserve development.ini --stop-daemon --pid-file=test_pserve.pid", app_scaffold, cd_folder="myapp")


def test_pytest(app_scaffold, test_db):
    """Create an application and see if py.test tests pass. """

    # Install test requirements
    execute_venv_command("cd myapp && pip install '.[test]'", app_scaffold, timeout=2*60)

    # Execute one functional test
    execute_venv_command("py.test --ini myapp/test.ini myapp/myapp/tests", app_scaffold, timeout=1*60)


def test_sdist(app_scaffold):
    """Create an application and see if sdist egg can be created. """
    execute_venv_command("cd myapp && python setup.py sdist", app_scaffold)


def test_app_syncdb(app_scaffold, dev_db):
    """Create an application and see if database is correctly created."""
    execute_venv_command("cd myapp && ws-sync-db development.ini", app_scaffold)


def test_shell(app_scaffold, dev_db):
    """Create an application and see if shell is started."""
    execute_venv_command("cd myapp && ws-shell development.ini", app_scaffold, wait_and_see=2.0)


def test_db_shell(app_scaffold, dev_db):
    """Create an application and see if shell is started."""
    execute_venv_command("cd myapp && ws-db-shell development.ini", app_scaffold, wait_and_see=2.0)


def test_migration(app_scaffold, dev_db):
    """Create an application, add a model and see if migrations are run."""

    with replace_file(os.path.join(app_scaffold, "myapp", "myapp", "models.py"), MODELS_PY):
        execute_venv_command("cd myapp && ws-alembic -c development.ini revision --autogenerate -m 'Added MyModel'", app_scaffold)
        execute_venv_command("cd myapp && ws-alembic -c development.ini upgrade head", app_scaffold)


def test_app_sanity_check_fail(app_scaffold, dev_db):
    """Create an application and see we don't start if migrations are not run."""
    execute_venv_command("cd myapp && pserve development.ini", app_scaffold, assert_exit=1)


def test_dump_db(app_scaffold, dev_db):
    """Test database dump."""
    execute_venv_command("cd myapp && ws-sync-db development.ini", app_scaffold)
    execute_venv_command("cd myapp && ws-dump-db development.ini", app_scaffold)


def test_tweens(app_scaffold, dev_db):
    """Test tweens command."""

    # TODO: Tweens should not really depent on database, but let's fix this later
    execute_venv_command("cd myapp && ws-sync-db development.ini", app_scaffold)
    execute_venv_command("cd myapp && ws-tweens development.ini", app_scaffold)


#: Migration test file
MODELS_PY="""
from websauna.system.model.meta import Base

class MyModel(Base):
    id = Column(Integer, autoincrement=True, primary_key=True)

"""