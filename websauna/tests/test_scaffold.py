"""Test different scaffold operations.

Rerunning these tests can be greatly sped up by creating a local Python package cache (wheelhouse)::

    bash websauna/tests/create_wheelhouse.bash

"""
import subprocess
import time
from contextlib import closing, contextmanager
import os
from tempfile import mkdtemp

import psycopg2
import pytest


VIRTUALENV = ["virtualenv-3.4", "venv"]

PSQL = "psql"


def print_subprocess_fail(worker, cmdline):
    print("{} output:".format(cmdline))
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


def execute_venv_command(cmdline, folder, timeout=5.0, wait_and_see=None, assert_exit=0):
    """Run a command in a specific folder using virtualenv created there.

    Assume virtualenv is under ``venv`` folder.

    :param wait_and_see: Wait this many seconds to see if app starts up.

    :param assert_exit: Assume exit code is this
    """

    assert os.path.exists(os.path.join(folder, "venv", "bin", "activate"))

    if type(cmdline) == list:
        cmdline = " ".join(cmdline)

    cmdline = ". {}/venv/bin/activate ; {}".format(folder, cmdline)

    # print("Executing {} in {}".format(cmdline, folder))

    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder, shell=True)

    if wait_and_see is not None:
        time.sleep(wait_and_see)
        worker.poll()

        if worker.returncode is not None:
            # Return code is set if the worker dies within the timeout
            print_subprocess_fail(worker, cmdline)
            raise AssertionError("could not start server like app: {}".format(cmdline))

        worker.kill()
        return 0
    else:
        try:
            worker.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            print_subprocess_fail(worker, cmdline)
            raise

    if worker.returncode != assert_exit:
        print_subprocess_fail(worker, cmdline)
        raise AssertionError("venv command did not properly exit: {} in {}. Got exit code {}, assumed {}".format(cmdline, folder, worker.returncode, assert_exit))

    return worker.returncode


def preload_wheelhouse(folder:str):
    """Speed up tests by loading Python packages from primed cache.

    Use ``create_wheelhouse.bash`` to prime the cache.

    :param folder: Temporary virtualenv installation
    """
    cache_folder = os.getcwd()

    if os.path.exists(os.path.join(cache_folder, "wheelhouse")):
        execute_venv_command("pip install {}/wheelhouse/*".format(cache_folder), folder, timeout=3*60)
    else:
        print("No preloaded Python package cache found")


def create_psq_db(request, dbname):
    """py.test fixture to createdb and destroy postgresql database on demand."""

    with closing(psycopg2.connect(database='postgres')) as conn:
        conn.autocommit = True
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT COUNT(*) FROM pg_database WHERE datname='{}'".format(dbname))

            if cursor.fetchone()[0] == 1:
                # Prior interrupted test run
                cursor.execute('DROP DATABASE ' + dbname)

            cursor.execute('CREATE DATABASE ' + dbname)

    def teardown():
        with closing(psycopg2.connect(database='postgres')) as conn:
            conn.autocommit = True
            with closing(conn.cursor()) as cursor:

                # http://blog.gahooa.com/2010/11/03/how-to-force-drop-a-postgresql-database-by-killing-off-connection-processes/
                cursor.execute("SELECT pg_terminate_backend(pid) from pg_stat_activity where datname='{}';".format(dbname))
                conn.commit()
                cursor.execute("SELECT COUNT(*) FROM pg_database WHERE datname='{}'".format(dbname))
                if cursor.fetchone()[0] == 1:
                    cursor.execute('DROP DATABASE ' + dbname)

    request.addfinalizer(teardown)


@contextmanager
def replace_file(path:str, content:str):
    """A context manager to temporary swap the content of a file.

    :param path: Path to the file
    :param content: New content as a text
    """
    backup = open(path, "rt").read()
    open(path, "wt").write(content)

    try:
        yield None
    finally:
        open(path, "wt").write(backup)


@pytest.fixture()
def dev_db(request):
    """Create PostgreSQL database myapcdp_dev and return its connection information."""
    return create_psq_db(request, "myapp_dev")


@pytest.fixture(scope='module')
def app_scaffold(request) -> str:
    """py.test fixture to create app scaffold.

    Create application and virtualenv for it. Run setup.py.

    :return: Path to a temporary folder. In this folder there is `venv` folder and `myapp` folder.
   """

    folder = mkdtemp(prefix="websauna_test_")

    websauna_folder = os.getcwd()

    execute_command(VIRTUALENV, folder)

    # PIP cannot handle pip -install .[test]
    # On some systems, the default PIP is too old and it doesn't seem to allow upgrade through wheelhouse
    execute_venv_command("pip install -U pip", folder, timeout=5*60)

    # Install cached PyPi packages
    preload_wheelhouse(folder)

    # Install websauna
    execute_venv_command("cd {} ; pip install -e .".format(websauna_folder), folder, timeout=5*60)

    # Create scaffold
    execute_venv_command("pcreate -s websauna_app myapp", folder)

    # Instal package created by scaffold
    content_folder = os.path.join(folder, "myapp")
    execute_venv_command("pip install -e {}".format(content_folder), folder, timeout=5*60)

    def teardown():
        # Clean any processes who still think they want to stick around. Namely: ws-shell doesn't die

        # This kills all processes referring to the temporary folder
        subprocess.call("pkill -SIGKILL -f {}".format(folder), shell=True)

    request.addfinalizer(teardown)

    return folder


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


def test_pytest(app_scaffold):
    """Create an application and see if py.test tests pass. """

    # Install test requirements
    execute_venv_command("cd myapp && pip install '.[test]'", app_scaffold, timeout=2*60)

    # Execute one functional test
    execute_venv_command("py.test --ini test.ini myapp/myapp/tests", app_scaffold)


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