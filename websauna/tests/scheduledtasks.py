"""Test tasks for the scheduler."""
import datetime
from websauna.system.task.celery import celery_app as celery
from websauna.system.core.redis import get_redis


@celery.task()
def delayed_test():
    connection = get_redis()
    connection.set("bar", "bar")

# Execute every second
@celery.task(name="foobar")
def redis_test_write():
    connection = get_redis()
    connection.set("foo", "foo")


# Execute every second
@celery.task(name="crashaxs")
def crash():
    raise RuntimeError("Test exception")

