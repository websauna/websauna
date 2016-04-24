"""Test addon scaffold operations.

Rerunning these tests can be greatly sped up by creating a local Python package cache (wheelhouse)::

    bash websauna/tests/create_wheelhouse.bash

"""
import time

import os
import pytest
from flaky import flaky

from .scaffold import execute_venv_command, insert_content_after_line
from .scaffold import replace_file
from .scaffold import create_psq_db
from .scaffold import app_scaffold  # noqa


@pytest.fixture()
def addon_dev_db(request):
    """Create PostgreSQL database myapcdp_dev and return its connection information."""
    return create_psq_db(request, "myaddon_dev")


@pytest.fixture()
def addon_test_db(request):
    return create_psq_db(request, "myaddon_test")


@pytest.fixture(scope='module')
def addon_scaffold(request, app_scaffold):
    """py.test fixture to create a new addon package.

    Reuse app_scaffold virtualenv.
    """

    folder = app_scaffold

    execute_venv_command("pcreate -s websauna_addon myaddon", folder)

    content_folder = os.path.join(folder, "websauna.myaddon")

    # Instal package created by scaffold
    execute_venv_command("cd websauna.myaddon && pip install -e .", folder, timeout=5 * 60)

    return folder


@flaky
def test_addon_pserve(addon_scaffold, addon_dev_db, browser):
    """Install and configure demo app for addon an and see if pserve starts."""

    # User models are needed to start the web server
    execute_venv_command("ws-sync-db development.ini", addon_scaffold, cd_folder="websauna.myaddon")
    execute_venv_command("ws-pserve development.ini --pid-file=test_pserve.pid", addon_scaffold, wait_and_see=3.0, cd_folder="websauna.myaddon")

    # Give pserve some time to wake up in CI
    time.sleep(4)

    try:

        # Make sure we get some sensible output from the server
        b = browser
        b.visit("http://localhost:6543/example-view")

        # See our scaffold home page loads and demo text is there
        assert b.is_element_present_by_css("#demo-text")

    finally:
        execute_venv_command("ws-pserve development.ini --stop-daemon --pid-file=test_pserve.pid", addon_scaffold, cd_folder="websauna.myaddon")


def test_addon_migration(addon_scaffold, addon_dev_db):
    """Create an addon, add a model and see if migrations are run and scripts created correctly."""

    with replace_file(os.path.join(addon_scaffold, "websauna.myaddon", "websauna", "myaddon", "models.py"), MODELS_PY):
        execute_venv_command("ws-alembic -c development.ini revision --autogenerate -m 'Added MyModel'", addon_scaffold, cd_folder="websauna.myaddon")
        execute_venv_command("ws-alembic -c development.ini upgrade head", addon_scaffold, cd_folder="websauna.myaddon")

        # Assert we got migration script for mymodel
        files = os.listdir(os.path.join(addon_scaffold, "websauna.myaddon", "alembic", "versions"))
        assert any("added_mymodel.py" in f for f in files), "Got files {}".format(files)


def test_addon_pytest(addon_scaffold, addon_test_db):
    """Create an addon and see if the default py.test tests pass. """

    # Install test requirements
    execute_venv_command("pip install '.[test]'", addon_scaffold, timeout=2 * 60, cd_folder="websauna.myaddon")

    # XXX: Looks like a new pip bug - we need to explicitly install websauna[test]? and dependencies are not respected
    execute_venv_command("pip install 'websauna[test]'", addon_scaffold, timeout=2 * 60, cd_folder="websauna.myaddon")

    # Execute one functional test
    execute_venv_command("py.test --ini test.ini websauna/myaddon/tests", addon_scaffold, timeout=1 * 60, cd_folder="websauna.myaddon")


def test_addon_sdist(addon_scaffold):
    """Create an addon and see if sdist egg can be created. """
    execute_venv_command("python setup.py sdist", addon_scaffold, cd_folder="websauna.myaddon")


def test_addon_integration(app_scaffold, addon_scaffold, addon_dev_db):
    """See that we can integrate websauna_addon to websauna_app scaffold.

    1. Create addon with models and migrations
    2. Make app using this addon
    3. See that app shell sees the models from the addon
    """
    with replace_file(os.path.join(addon_scaffold, "websauna.myaddon", "websauna", "myaddon", "models.py"), MODELS_PY):
        with insert_content_after_line(os.path.join(app_scaffold, "myapp", "myapp", "__init__.py"), ADDON_INSTALLED_INITIALIZER, "def run"):
            # path = os.path.join(app_scaffold, "myapp", "myapp", "__init__.py")
            # print(path)
            exit_code, output, stderr = execute_venv_command("echo 'quit()' | ws-shell conf/development.ini", app_scaffold, cd_folder="myapp", timeout=30)
            assert "MyModel" in output


#: Migration test file
MODELS_PY = """
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.ext.declarative.base import _declarative_constructor

class MyModel:

    __tablename__ = "mymodel"
    id = Column(Integer, autoincrement=True, primary_key=True)

    # Because we cannot inherit from Base we need to set up the default SQLAlchemy model constructor in this special way
    __init__ = _declarative_constructor

"""

#: Initializer file snipped when addon has been installed
ADDON_INSTALLED_INITIALIZER = """

    def include_addons(self):
        self.config.include("websauna.myaddon")

"""