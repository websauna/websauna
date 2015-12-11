"""Test different scaffold operations."""
import subprocess
import time

import os
import shutil

import pytest
from tempfile import mkdtemp


#: Python command for creating a virtualenv (platform specific)
VIRTUALENV = ["virtualenv-3.4", "venv"]


def print_subprocess_fail(worker, cmdline):
    print("pcreate output:")
    print(worker.stdout.read().decode("utf-8"))
    print(worker.stderr.read().decode("utf-8"))


def execute_command(cmdline, folder):
    """Run a command in a specific folder."""
    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder)

    worker.wait(timeout=5.0)

    if worker.returncode != 0:
        print_subprocess_fail(worker, cmdline)
        raise AssertionError("scaffold command did not properly exit: {}".format(" ".join(cmdline)))

    return worker.returncode


def execute_command(cmdline, folder):
    """Run a command in a specific folder."""
    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder)

    worker.wait(timeout=5.0)

    if worker.returncode != 0:
        print_subprocess_fail(worker, cmdline)
        raise AssertionError("scaffold command did not properly exit: {}".format(" ".join(cmdline)))

    return worker.returncode


def execute_venv_command(cmdline, folder, timeout=5.0, wait_and_see=None):
    """Run a command in a specific folder using virtualenv created there.

    Assume virtualenv is under ``venv`` folder.

    :param wait_and_see: Wait this many seconds to see if app starts up.
    """

    assert os.path.exists(os.path.join(folder, "venv", "bin", "activate"))

    if type(cmdline) == list:
        cmdline = " ".join(cmdline)

    cmdline = ". {}/venv/bin/activate ; {}".format(folder, cmdline)

    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder, shell=True)

    if wait_and_see is not None:
        time.sleep(wait_and_see)
        if worker.returncode is not None:
            print_subprocess_fail(worker, cmdline)
            raise AssertionError("could not start server like app: {}".format(cmdline))
        worker.terminate()
        return 0
    else:
        worker.wait(timeout=timeout)

    if worker.returncode != 0:
        print_subprocess_fail(worker, cmdline)
        raise AssertionError("venv command did not properly exit: {} in {}".format(cmdline, folder))

    return worker.returncode


@pytest.fixture(scope='module')
def app_scaffold(request) -> str:
    """py.test fixture to create app scaffold.

    Create application and virtualenv for it. Run setup.py.
    """

    folder = mkdtemp(prefix="websauna_test_")
    content_folder = os.path.join(folder, "myapp")
    websauna_folder = os.getcwd()

    execute_command(["pcreate", "-s", "websauna_app", "myapp"], folder)
    execute_command(VIRTUALENV , content_folder)

    # Install websauna
    # Try to run through all PyPi installation in 2 minutes
    execute_venv_command("cd {} ; python setup.py develop".format(websauna_folder), content_folder, timeout=2*60)

    # Now install the scaffold itself
    execute_venv_command(["python", "setup.py", "develop"], content_folder, timeout=2*60)

    def teardown():
        pass
        # if return_code != 0:
            # Leave files around on a failure so you can explore what went wrong
        #    shutil.rmtree(folder)

    request.addfinalizer(teardown)

    return content_folder


def test_app_pserve(app_scaffold):
    """Create an application and see if pserve starts. """

    cmdline = ["pserve", "development.ini"]
    execute_venv_command(cmdline, app_scaffold, wait_and_see=10.0)


def test_app_pytest(app_scaffold):
    """Create an application and see if py.test tests pass. """

    cmdline = ["py.test", "--ini", "test.ini", "myapp"]
    execute_venv_command(cmdline, app_scaffold)


def test_app_sdist():
    """Create an application and see if sdist egg can be created. """


def test_app_initializedb():
    """Create an application and see if database is correctly created."""


def test_app_shell():
    """Create an application and see if shell is started."""


def test_app_migration():
    """Create an application and see if migrations are run."""


def test_app_sanity_check_fail():
    """Create an application and see we don't start if migrations are not run."""


def test_app_add_adminl():
    """Create an application and add an admin interface."""