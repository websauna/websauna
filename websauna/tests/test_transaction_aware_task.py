"""Celery tasks and transaction awareness tests.

To debug Celery worker, disable Celery launching, re(run) test with Celery worker, running in another terminal::

    pkill -f celery
    celery worker -A websauna.tests.test_transaction_aware_task.test_celery_app --ini test.ini --loglevel DEBUG

    sleep 4
    py.test websauna -s --ini=test.ini -x -k test_transaction_aware_task_success

Or turn of eager celery setting hardcoded below.

"""

import logging
import subprocess
import time
from optparse import make_option
import os
import pyramid
import pytest
import transaction
from celery import Celery
from celery import signals
from pyramid.paster import bootstrap
from pyramid.settings import asbool
from pyramid.testing import DummyRequest
import pyramid_celery
from pyramid_celery.loaders import INILoader
from websauna.system.task import TransactionalTask
from websauna.system.task import RequestAwareTask
from websauna.system.user.utils import get_user_class

logger = logging.getLogger(__name__)

# Hardcode here for a now as passing command line option to Celery just for executing seems to be bit too much boilerplate
test_celery_app = Celery("websauna_test")

# class Config:
#     BROKER_URL="redis://localhost:6379/15"
#     CELERY_ALWAYS_EAGER=False
#     CELERY_RESULT_SERIALIZER="json"
#     CELERY_TASK_SERIALIZER="json"
#     CELERY_ACCEPT_CONTENT=["json", "msgpack"]
#
#
# test_celery_app.config_from_object(Config)
#
# Unfortunately we need to do this due to Celery globals
old_celery = pyramid_celery.celery_app

test_celery_app.user_options['preload'].add(
    make_option(
        '-i', '--ini',
        default=None,
        help='Paste ini configuration file.'),
)

test_celery_app.user_options['preload'].add(
    make_option(
        '--ini-var',
        default=None,
        help='Comma separated list of key=value to pass to ini'),
)


def setup_app(registry, ini_location):
    celery_app = test_celery_app
    loader = INILoader(celery_app, ini_file=ini_location)
    celery_config = loader.read_configuration()

    if asbool(celery_config.get('USE_CELERYCONFIG', False)) is True:
        config_path = 'celeryconfig'
        celery_app.config_from_object(config_path)
    else:
        celery_app.config_from_object(celery_config)

    celery_app.conf.update({'PYRAMID_REGISTRY': registry})

    return celery_app


@signals.user_preload_options.connect
def _on_preload_parsed(options, **kwargs):
    """This is run when celery worker process boots up."""
    ini_location = options['ini']
    ini_vars = options['ini_var']

    if ini_location is None:
        print('You must provide the paste --ini argument')
        exit(-1)

    options = {}
    if ini_vars is not None:
        for pairs in ini_vars.split(','):
            key, value = pairs.split('=')
            options[key] = value

        env = bootstrap(ini_location, options=options)
    else:
        env = bootstrap(ini_location)

    registry = env['registry']
    setup_app(registry, ini_location)


@pytest.fixture(scope='module')
def celery_worker(request, init):
    """py.test fixture to shoot up Celery worker process with our test config."""

    ini_file = os.path.join(os.path.dirname(__file__), "..", "..", "test.ini")

    setup_app(init.config.registry, ini_file)

    cmdline = ["ws-celery", "worker", "-A", "websauna.tests.test_transaction_aware_task.test_celery_app", "--ini", ini_file, "--loglevel", "DEBUG"]

    logger.info("Running celery worker: %s", cmdline)

    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(4.0)

    worker.poll()
    if worker.returncode is not None:
        raise AssertionError("Celery worker process did not start up: {}".format(" ".join(cmdline)))

    def teardown():
        worker.terminate()
        # XXX: Hard to capture this only on failure for now
        # print(worker.stdout.read().decode("utf-8"))
        # print(worker.stderr.read().decode("utf-8"))

    request.addfinalizer(teardown)

    return worker.pid


def setup_celery(init):
    """Setup Celery instance which has a lifetime of a test."""

    # XXX: Don't know why we need to force this again despite the settings... something internal to Celery stringifie this setting, resulting to false true. Tried to figure out for two hours, gave up, asking world to help to replace Celery with something else.
    test_celery_app.conf.CELERY_ALWAYS_EAGER = True

    test_celery_app.pyramid_config = init.config

    # We need to setup thread local request which binds to our test transaction manager
    request = DummyRequest()
    request.tm = transaction.manager
    pyramid.threadlocal.manager.push({'request': request})

    return test_celery_app, request


@test_celery_app.task(base=TransactionalTask)
def success_task(request, user_id):
    # TODO: Eliminate global dbsession
    dbsession = request.dbsession
    registry = request.registry

    User = get_user_class(registry)
    u = dbsession.query(User).get(user_id)
    u.username = "set by celery"


@test_celery_app.task(base=TransactionalTask)
def success_task_never_called(request, user_id):
    # TODO: Eliminate global dbsession
    dbsession = request.dbsession

    request = test_celery_app
    registry = request.registry

    User = get_user_class(registry)
    u = dbsession.query(User).get(user_id)
    u.username = "set by celery"


@test_celery_app.task(base=TransactionalTask)
def failure_task(request, user_id):
    # TODO: Eliminate global dbsession
    dbsession = request.dbsession
    registry = request.registry

    User = get_user_class(registry)
    u = dbsession.query(User).get(user_id)
    u.username = "set by celery"
    raise RuntimeError("Exception raised")


@test_celery_app.task(base=RequestAwareTask)
def request_task(request, user_id):
    # Run transaction manually
    with transaction.manager:
        # TODO: Eliminate global dbsession
        dbsession = request.dbsession
        registry = request.registry

        User = get_user_class(registry)
        u = dbsession.query(User).get(user_id)
        u.username = "set by celery"


def test_transaction_aware_task_success(celery_worker, init, dbsession):
    """Test that transaction aware task does not fail."""

    celery_app, request = setup_celery(init)
    User = get_user_class(init.config.registry)

    with request.tm:
        # Do a dummy database write
        u = User(username="test", email="test@example.com")
        dbsession.add(u)

    with request.tm:
        # Do a dummy database write
        u = dbsession.query(User).get(1)

        success_task.apply_async(args=[request, u.id])
        # Let the task travel in Celery queue
        time.sleep(1.0)

        # Task should not fire unless we exit the transaction
        assert u.username != "set by celery"

    # Let the transaction commit
    time.sleep(0.5)

    # Task has now fired after transaction was committed
    with transaction.manager:
        u = dbsession.query(User).get(1)
        assert u.username == "set by celery"


def test_transaction_aware_task_fail(celery_worker, init, dbsession):
    """Test that transaction that do not commit do not run tasks."""

    celery_app, request = setup_celery(init)

    with request.tm:
        # Do a dummy database write
        User = get_user_class(init.config.registry)
        u = User(username="test", email="test@example.com")
        dbsession.add(u)

    try:
        # Tasks do not execute if transaction is aborted because of exception
        with request.tm:
            assert dbsession.query(User).count() == 1
            assert dbsession.query(User).get(1).username == "test"
            success_task_never_called.apply_async(args=[request, 1])
            raise RuntimeError("aargh")
    except RuntimeError:
        pass

    # Let the transaction commit (which should not happen)
    time.sleep(0.5)

    # Because of exception, Celery never fires
    with transaction.manager:
        u = dbsession.query(User).get(1)
        assert u.username == "test"


def test_transaction_aware_task_throws_exception(celery_worker, init, dbsession):
    """Test that transaction aware task does not commit if exception is thrown.."""

    celery_app, request = setup_celery(init)

    with request.tm:
        # Do a dummy database write
        User = get_user_class(init.config.registry)
        u = User(username="test", email="test@example.com")
        dbsession.add(u)
        dbsession.flush()

        failure_task.apply_async(args=[request, u.id])
        # Let the task travel in Celery queue
        time.sleep(0.5)

        # Task should not fire unless we exit the transaction
        assert u.username != "set by celery"

    # Let the transaction commit
    time.sleep(0.5)

    # Task has now fired after transaction was committed
    with transaction.manager:
        u = dbsession.query(User).get(1)
        assert u.username == "test"


def test_request_aware_task_success(celery_worker, init, dbsession):
    """Test that RequestAwareTask executes."""

    celery_app, request = setup_celery(init)
    User = get_user_class(init.config.registry)

    with request.tm:
        # Do a dummy database write
        u = User(username="test", email="test@example.com")
        dbsession.add(u)

    with request.tm:
        # Do a dummy database write
        u = dbsession.query(User).get(1)

        request_task.apply_async(kwargs={"request": request, "user_id": u.id})
        # Let the task travel in Celery queue
        time.sleep(1.0)

        # Task should not fire unless we exit the transaction
        assert u.username != "set by celery"

    # Let the transaction commit
    time.sleep(0.5)

    # Task has now fired after transaction was committed
    with transaction.manager:
        u = dbsession.query(User).get(1)
        assert u.username == "set by celery"

