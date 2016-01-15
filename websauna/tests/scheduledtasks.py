"""Test tasks for the scheduler."""
import datetime

from websauna.system.task import RequestAwareTask
from websauna.system.task.celery import celery_app as celery
from websauna.system.core.redis import get_redis


# Execute every second
@celery.task(name="foobar", base=RequestAwareTask)
def redis_test_write(request):
    registry = request.registry
    connection = get_redis(registry)
    connection.set("foo", "foo")


# Execute every second
@celery.task(name="crashaxs")
def crash():
    raise RuntimeError("Test exception")

