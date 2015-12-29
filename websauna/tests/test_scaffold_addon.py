"""Test different scaffold operations.

Rerunning these tests can be greatly sped up by creating a local Python package cache (wheelhouse)::

    bash websauna/tests/create_wheelhouse.bash

"""

import os
import pytest

from .scaffold import execute_venv_command
from .scaffold import replace_file
from .scaffold import create_psq_db
from .scaffold import app_scaffold  # noqa


@pytest.fixture()
def addon_dev_db(request):
    """Create PostgreSQL database myapcdp_dev and return its connection information."""
    return create_psq_db(request, "myaddon_dev")


@pytest.fixture(scope='module')
def addon_scaffold(request, app_scaffold):
    """py.test fixture to create a new addon package.

    Reuse app_scaffold virtualenv.
    """

    folder = app_scaffold

    execute_venv_command("pcreate -s websauna_addon myaddon", folder)

    content_folder = os.path.join(folder, "websauna.myaddon")

    # Instal package created by scaffold
    execute_venv_command("pip install -e {}".format(content_folder), folder, timeout=5*60)

    return folder


def test_pserve(addon_scaffold, addon_dev_db, browser):
    """Install and configure demo app for addon an and see if pserve starts."""

    # User models are needed to start the web server
    execute_venv_command("ws-sync-db development.ini", addon_scaffold, cd_folder="websauna.myaddon")
    execute_venv_command("pserve development.ini --pid-file=test_pserve.pid", addon_scaffold, wait_and_see=3.0, cd_folder="websauna.myaddon")

    try:

        # Make sure we get some sensible output from the server
        b  = browser
        b.visit("http://localhost:6543/example-view")

        # See our scaffold home page loads and demo text is there
        assert b.is_element_present_by_css("#demo-text")

    finally:
        execute_venv_command("pserve development.ini --stop-daemon --pid-file=test_pserve.pid", addon_scaffold, cd_folder="websauna.myaddon")
