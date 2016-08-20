"""Test tasks for the scheduler."""

from websauna.system.task import RequestAwareTask
from websauna.system.task.celery import task
from websauna.system.core.redis import get_redis


# Configured to be executed every second in scheduler-test.ini
@task(name="foobar", bind=True, base=RequestAwareTask)
def redis_test_write(self):
    request = self.request.request
    connection = get_redis(request)
    connection.set("foo", "foo")


# Execute every second
@task(name="crashaxs")
def crash():
    raise RuntimeError("Test exception")

