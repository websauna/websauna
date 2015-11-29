"""Celery tasks and transaction awareness tests.

Re(run) test (Celery might need to be nuked between failed test runs)::

    pkill -f celery
    nohup celery worker -A websauna.tests.test_transaction_aware_task.test_celery_app --ini test.ini --loglevel DEBUG > celery-worker.log &
    sleep 4
    py.test websauna -s --ini=test.ini -x -k test_transaction_aware_task_success

    # Not needed for now
    #     nohup celery beat -A websauna.tests.test_transaction_aware_task.test_celery_app --ini test.ini > celery-beat.log &
"""
import configparser
import time
from optparse import make_option

import pyramid
import pytest
import transaction

import psutil
from celery import Celery
from celery import signals
from pyramid.testing import DummyRequest
import pyramid_celery
from pyramid_celery import on_preload_parsed
from websauna.system.task.transactionawaretask import TransactionAwareTask
from websauna.system.user.utils import get_user_class
from websauna.system.model import DBSession



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
pyramid_celery.celery_app = test_celery_app


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


@signals.user_preload_options.connect
def _on_preload_parsed(options, **kwargs):
    """This is run when celery worker process boots up."""
    on_preload_parsed(options, **kwargs)


def is_celery_running():
    """Don't try to run any Celery tests unless Celery worker is running."""
    marker = "celery worker -A websauna.tests.test_transaction_aware_task.test_celery_app"
    for proc in psutil.process_iter():
        try:
            if marker in " ".join(proc.cmdline()):
                return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

    return False


def setup_celery(init):
    """Setup Celery instance which has a lifetime of a test."""

    # XXX: Don't know why we need to force this again despite the settings... something internal to Celery stringifie this setting, resulting to false true. Tried to figure out for two hours, gave up, asking world to help to replace Celery with something else.
    test_celery_app.conf.CELERY_ALWAYS_EAGER = False

    test_celery_app.pyramid_config = init.config

    # We need to setup thread local request
    request = DummyRequest()
    request.tm = transaction.manager
    pyramid.threadlocal.manager.get()['request'] = request

    return test_celery_app, request


@test_celery_app.task(base=TransactionAwareTask)
def success_task(request, user_id):

    # TODO: Eliminate global dbsession
    dbsession = DBSession
    registry = request.registry

    User = get_user_class(registry)
    u = dbsession.query(User).get(user_id)
    u.username = "set by celery"


@test_celery_app.task(base=TransactionAwareTask)
def failure_task(request, user_id):

    # TODO: Eliminate global dbsession
    dbsession = DBSession
    registry = request.registry

    User = get_user_class(registry)
    u = dbsession.query(User).get(user_id)
    u.username = "set by celery"
    raise RuntimeError("Exception raised")


@pytest.mark.skipif(not is_celery_running(), reason="No test Celery worker processes running")
def test_transaction_aware_task_success(init, dbsession):
    """Test that transaction aware task does not fail."""

    celery_app, request = setup_celery(init)

    with request.tm:
        # Do a dummy database write
        User = get_user_class(init.config.registry)
        u = User(username="test", email="test@example.com")
        dbsession.add(u)
        dbsession.flush()

        success_task.apply_async(args=[u.id])
        # Let the task travel in Celery queue
        time.sleep(0.5)

        # Task should not fire unless we exit the transaction
        assert u.username != "set by celery"

    # Let the transaction commit
    time.sleep(0.5)

    # Task has now fired after transaction was committed
    with transaction.manager:
        u = dbsession.query(User).get(1)
        assert u.username == "set by celery"


@pytest.mark.skipif(not is_celery_running(), reason="No test Celery worker processes running")
def test_transaction_aware_task_fail(init, dbsession):
    """Test that transaction that do not commit do not run tasks."""

    celery_app, request = setup_celery(init)

    with request.tm:
        # Do a dummy database write
        User = get_user_class(init.config.registry)
        u = User(username="test", email="test@example.com")
        dbsession.add(u)
        dbsession.flush()

    try:
        # Tasks do not execute if transaction is aborted because of exception
        with request.tm:
            success_task.apply_async(args=[1])
            raise RuntimeError("aargh")
    except RuntimeError:
        pass

    # Let the transaction commit (which should not happen)
    time.sleep(0.5)

    # Because of exception, Celery never fires
    with transaction.manager:
        u = dbsession.query(User).get(1)
        assert u.username == "test"


@pytest.mark.skipif(not is_celery_running(), reason="No test Celery worker processes running")
def test_transaction_aware_task_throws_exception(init, dbsession):
    """Test that transaction aware task does not commit if exception is thrown.."""

    celery_app, request = setup_celery(init)

    with request.tm:
        # Do a dummy database write
        User = get_user_class(init.config.registry)
        u = User(username="test", email="test@example.com")
        dbsession.add(u)
        dbsession.flush()

        failure_task.apply_async(args=[u.id])
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
