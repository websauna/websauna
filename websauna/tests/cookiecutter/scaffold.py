"""Scaffold test utility functions."""
# Standard Library
import os
import subprocess
import sys
import time
import typing as t
from contextlib import closing
from contextlib import contextmanager
from tempfile import mkdtemp

# SQLAlchemy
import psycopg2

import pytest
from cookiecutter.main import cookiecutter


PYTHON_INTERPRETER = 'python{major}.{minor}'.format(
    major=sys.version_info.major,
    minor=sys.version_info.minor
)


def print_subprocess_fail(worker, cmdline):
    print('{cmdline} output:'.format(cmdline=cmdline))
    for output in (worker.stdout, worker.stderr):
        print(output.read().decode('utf-8'))


def execute_command(cmdline: t.List, folder: str, timeout=5.0):
    """Run a command in a specific folder."""
    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder)
    try:
        worker.wait(timeout)
    except subprocess.TimeoutExpired as e:
        print_subprocess_fail(worker, cmdline)
        raise AssertionError('execute_command did not properly exit') from e

    if worker.returncode != 0:
        print_subprocess_fail(worker, cmdline)
        raise AssertionError('scaffold command did not properly exit: {cmdline}'.format(cmdline=' '.join(cmdline)))

    return worker.returncode


def execute_venv_command(cmdline, cwd, timeout=15.0, wait_and_see=None, assert_exit=0, cd_folder=None):
    """Run a command in a specific folder using virtualenv created there.

    Assume virtualenv is under ``venv`` folder.

    :param cwd: Base folder.
    :param timeout: Command timeout.
    :param wait_and_see: Wait this many seconds to see if app starts up.
    :param assert_exit: Assume exit code is this
    :param cd_folder: cd to this folder before executing the command (relative to folder)
    :return: tuple (exit code, stdout, stderr)
    """
    activate_venv = os.path.join(cwd, 'venv', 'bin', 'activate')
    assert os.path.exists(activate_venv), ' '.join(os.listdir(os.path.join(cwd, 'venv', 'bin')))

    if type(cmdline) == list:
        cmdline = ' '.join(cmdline)

    cd_cmd = cwd
    if cd_folder is not None:
        cd_cmd = '{cwd}/{cd_folder}'.format(cwd=cwd, cd_folder=cd_folder)

    cmdline = ". {activate_venv}; {cmdline}".format(activate_venv=activate_venv, cmdline=cmdline)

    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cd_cmd, shell=True)

    if wait_and_see is not None:
        time.sleep(wait_and_see)
        worker.poll()

        if worker.returncode is not None:
            # Return code is set if the worker dies within the timeout
            print_subprocess_fail(worker, cmdline)
            raise AssertionError('could not start server like app: {cmdline}'.format(cmdline=cmdline))

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
        raise AssertionError(
            'venv command did not properly exit: {cmdline} in {cwd}. Got exit code {returncode}, assumed {assert_exit}'.format(
                cmdline=cmdline,
                cwd=cwd,
                returncode=worker.returncode,
                assert_exit=assert_exit
            )
        )

    return (worker.returncode, worker.stdout.read().decode('utf-8'), worker.stderr.read().decode('utf-8'))


def preload_wheelhouse(folder: str):
    """Speed up tests by loading Python packages from primed cache.

    Use ``create_wheelhouse.bash`` to prime the cache.

    :param folder: Temporary virtualenv installation
    """
    cache_folder = os.getcwd()
    wheelhouse_folder = os.path.join(
        cache_folder,
        'wheelhouse', 'python{major}.{minor}'.format(
            major=sys.version_info.major,
            minor=sys.version_info.minor
        )
    )
    if os.path.exists(wheelhouse_folder):
        execute_venv_command(
            "pip install {wheelhouse_folder}/*".format(wheelhouse_folder=wheelhouse_folder),
            folder,
            timeout=3 * 60
        )
    else:
        print('No preloaded Python package cache found')


def create_psq_db(request, dbname, dsn=''):
    """py.test fixture to createdb and destroy postgresql database on demand."""
    if not dsn:
        dsn = 'dbname=postgres'
    with closing(psycopg2.connect(dsn)) as conn:
        conn.autocommit = True
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT COUNT(*) FROM pg_database WHERE datname='{dbname}'".format(dbname=dbname))

            if cursor.fetchone()[0] == 1:
                # Prior interrupted test run
                cursor.execute('DROP DATABASE ' + dbname)

            cursor.execute('CREATE DATABASE ' + dbname)

    def teardown():
        with closing(psycopg2.connect(dsn)) as conn:
            conn.autocommit = True
            with closing(conn.cursor()) as cursor:

                # http://blog.gahooa.com/2010/11/03/how-to-force-drop-a-postgresql-database-by-killing-off-connection-processes/
                cursor.execute("SELECT pg_terminate_backend(pid) from pg_stat_activity where datname='{dbname}'".format(dbname=dbname))
                conn.commit()
                cursor.execute("SELECT COUNT(*) FROM pg_database WHERE datname='{dbname}'".format(dbname=dbname))
                if cursor.fetchone()[0] == 1:
                    cursor.execute('DROP DATABASE ' + dbname)

    request.addfinalizer(teardown)


@contextmanager
def replace_file(path: str, content: str):
    """A context manager to temporary swap the content of a file.

    :param path: Path to the file
    :param content: New content as a text
    """
    backup = open(path, 'rt').read()
    open(path, 'wt').write(content)

    try:
        yield None
    finally:
        open(path, 'wt').write(backup)


@contextmanager
def insert_content_after_line(path: str, content: str, marker: str):
    """Add piece to text to a text file after a line having a marker string on it."""
    backup = open(path, "rt").read()
    try:
        # Replaces stdout
        out = open(path, 'wt')
        for line in backup.split("\n"):
            if marker in line:
                print(content, file=out)
            print(line, file=out)
        out.close()
        yield None
    finally:
        open(path, 'wt').write(backup)


@pytest.fixture(scope='session')
def cookiecutter_config(tmpdir_factory) -> str:
    """py.test fixture to generate a tmp config file for cookiecutter.

    :return: Path to cookiecutter config file.
   """
    user_dir = tmpdir_factory.mktemp('user_dir')
    cookiecutters_dir = user_dir.mkdir('cookiecutters')
    replay_dir = user_dir.mkdir('cookiecutter_replay')
    USER_CONFIG = '''cookiecutters_dir: "{cookiecutters_dir}"\nreplay_dir: "{replay_dir}"'''
    config_text = USER_CONFIG.format(
        cookiecutters_dir=cookiecutters_dir,
        replay_dir=replay_dir,
    )
    config_file = user_dir.join('config')

    config_file.write_text(config_text, encoding='utf8')
    return str(config_file)


@pytest.fixture(scope='session')
def app_scaffold(request, cookiecutter_config) -> str:
    """py.test fixture to create app scaffold.

    Create application and virtualenv for it. Run setup.py.

    :return: Path to a temporary folder. In this folder there is `venv` folder and `myapp` folder.
   """

    folder = mkdtemp(prefix='websauna_test_')

    websauna_folder = os.getcwd()
    execute_command([PYTHON_INTERPRETER, '-m', 'venv', 'venv'], folder, timeout=30)

    # Make sure we have a recent pip version
    execute_venv_command('pip install -U pip', folder, timeout=5 * 60)

    # Install cached PyPi packages
    preload_wheelhouse(folder)

    # Install websauna
    cmdline = 'pip install -e {folder}[notebook,utils]'.format(folder=websauna_folder)
    execute_venv_command(cmdline, folder, timeout=5 * 60)

    # Create Websauna app, using cookiecutter, from template cookiecutter-websauna-app
    extra_context = {
        'full_name': 'Websauna Team',
        'email': 'developers@websauna.org',
        'company': 'Websauna',
        'github_username': 'websauna',
        'project_name': 'Websauna: News portal',
        'project_short_description': 'Websauna news portal application.',
        'tags': 'python package websauna pyramid',
        'repo_name': 'my.app',
        'namespace': 'my',
        'package_name': 'app',
        'release_date': 'today',
        'year': '2017',
        'version': '1.0.0a1',
        'create_virtualenv': 'No'
    }
    template = 'https://github.com/websauna/cookiecutter-websauna-app/archive/master.zip'
    cookiecutter(
        template,
        no_input=True,
        extra_context=extra_context,
        output_dir=folder,
        config_file=cookiecutter_config
    )

    # Install the package created by cookiecutter template
    content_folder = os.path.join(folder, extra_context['repo_name'])
    execute_venv_command('pip install -e {0}'.format(content_folder), folder, timeout=5 * 60)

    def teardown():
        # Clean any processes who still think they want to stick around. Namely: ws-shell doesn't die

        # This kills all processes referring to the temporary folder
        subprocess.call('pkill -SIGKILL -f {cwd}'.format(cwd=folder), shell=True)

    request.addfinalizer(teardown)
    return folder


def start_ws_pserve(config: str, cwd: str, wait_and_see: float=5.0, cd_folder=''):
    """Simulate starting ws-pserve command from the command line inside the virtualenv.

    :param config: Configuration.
    :param cwd: Set current working directory
    :param wait_and_see: Seconds to see if the server comes up
    :param cd_folder: cd to this folder before executing the command (relative to folder)
    """

    # Clean up all prior processes
    import psutil
    import signal

    # http://stackoverflow.com/a/20691431/315168
    for proc in psutil.process_iter():
        try:
            for conns in proc.connections(kind='inet'):
                if conns.laddr[1] == 6543:
                    print('Killing a proc blocking the port', proc)
                    proc.send_signal(signal.SIGKILL)
                    time.sleep(0.5)
                    continue
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

    # Run pserve inside the virtualenv
    activate_venv = os.path.join(cwd, 'venv', 'bin', 'activate')
    cmdline = '. {activate_venv}; cd {cd_folder} && pserve {config}'.format(
        activate_venv=activate_venv,
        cd_folder=cd_folder,
        config=config,
    )
    print(cmdline)
    worker = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

    time.sleep(wait_and_see)
    worker.poll()

    if worker.returncode is not None:
        # Return code is set if the worker dies within the timeout
        print_subprocess_fail(worker, cmdline)
        raise AssertionError('Could not pserve: {cmdline}'.format(cmdline=cmdline))

    return worker
