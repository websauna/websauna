"""See that beat runs scheduled tasks correctly."""

# Standard Library
import os
import time
import pytest
from flaky import flaky

# Websauna
from websauna.system.core.redis import get_redis


@pytest.fixture(scope='module')
def run_worker_and_beat(request, task_ini_file, watcher_getter):
    ini_file = "ws://{}".format(task_ini_file)
    pid_file = "/tmp/celerybeat.pid"

    return watcher_getter(
        name='ws-celery',
        arguments=[ini_file, '--', 'worker', '-B', '--pidfile={}'.format(pid_file)],
        checker=lambda: os.path.exists(pid_file),
        request=request,
    )


@flaky
def test_celery_beat(init, run_worker_and_beat):
    """Scheduled tasks run properly on the celery worker + celery beat process."""

    # Reset test database
    redis = get_redis(init.config.registry)
    redis.delete("foo", "bar")

    foo = "no read"
    deadline = time.time() + 10
    while time.time() < deadline:
        redis = get_redis(init.config.registry)
        # scheduledtasks.ticker should beat every second and reset values in Redis
        foo = redis.get("foo")
        if foo:
            break
        time.sleep(0.5)

    assert foo == b"xoo"  # Set back by its original value by 1 second beat
