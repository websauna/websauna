"""Test tasks for the scheduler."""
import datetime
from pyramid_celery import celery_app as app
from websauna.system.core.redis import get_redis


@app.task()
def delayed_test():
    connection = get_redis()
    connection.set("bar", "bar")

# Execute every second
@app.task(name="foobar")
def redis_test_write():
    connection = get_redis()
    connection.set("foo", "foo")



# Execute every second
@app.task(name="crashaxs")
def crash():
    raise RuntimeError("Test exception")

