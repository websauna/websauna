"""Test tasks for the scheduler."""
import transaction

from websauna.system import DemoInitializer
from websauna.system.task.tasks import ScheduleOnCommitTask
from websauna.system.task.tasks import RetryableTransactionTask
from websauna.system.task.tasks import task
from websauna.system.core.redis import get_redis


from websauna.system.user.models import User


# Configured to be executed every second in scheduler-test.ini
@task(name="foobar", bind=True)
def redis_test_write(self):
    request = self.request.request
    connection = get_redis(request)
    connection.set("foo", "foo")


@task(name="crashaxs")
def crash():
    raise RuntimeError("Test exception")


@task(base=RetryableTransactionTask, bind=True)
def modify_username(self, user_id):
    """A demo task we use to detect that Celery tasks write database changes correctly."""
    print(self)
    request = self.request.request
    dbsession = request.dbsession

    u = dbsession.query(User).get(user_id)
    u.username = "set by celery"


@task(base=RetryableTransactionTask)
def modify_username_abort_by_exception(self, user_id):
    """We never commit as exception is raisen."""
    request = self.request.request
    dbsession = request.dbsession

    u = dbsession.query(User).get(user_id)
    u.username = "set by celery"  # This change should not commit
    raise RuntimeError("Exception raised")


@task(base=ScheduleOnCommitTask, bind=True)
def modify_username_manual_transaction(self, user_id):
    """Example of a manual transaction management within a task."""
    request = self.request.request

    with request.tm:

        dbsession = request.dbsession

        u = dbsession.query(User).get(user_id)
        u.username = "set by celery"


class SchedulerInitializer(DemoInitializer):
    """Entry point for tests stressting task functionality."""

    def configure_tasks(self):
        self.config.scan("websauna.tests.demotasks")


def main(global_config, **settings):
    return SchedulerInitializer.bootstrap(global_config)
