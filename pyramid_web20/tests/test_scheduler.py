import subprocess
import time
import os

from pyramid_web20 import Initializer
from pyramid_web20.system.core.redis import get_redis
from pyramid_web20.utils.configincluder import IncludeAwareConfigParser

from pyramid_web20.tests import scheduledtasks


def test_run_scheduled(pyramid_testing):
    """Scheduled tasks run properly on the celery worker + celery beat process."""

    ini_file = os.path.join(os.path.dirname(__file__), "scheduler-test.ini")

    cmdline = ["celery", "worker", "-A", "pyramid_web20.system.celery.celery_app", "--ini", ini_file]

    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2.0)

    worker.poll()
    if worker.returncode is not None:
        raise AssertionError("Scheduler process did not start up: {}".format(" ".join(cmdline)))

    cmdline = ["celery", "beat", "-A", "pyramid_web20.system.celery.celery_app", "--ini", ini_file]
    beat = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(1.0)
    beat.poll()
    if beat.returncode is not None:
        worker.terminate()
        AssertionError("Beat process did not start up")

    try:
        # Reset test database
        redis = get_redis()
        redis.delete("foo", "bar")
        scheduledtasks.delayed_test.delay()

        # scheduledtasks.ticker should beat every second and reset values in Redis
        time.sleep(2)

        redis = get_redis()
        foo = redis.get("foo")
        bar = redis.get("bar")

        assert beat.returncode is None
        assert worker.returncode is None
        assert foo == b"foo"
        assert bar == b"bar"

    finally:
        worker.terminate()
        beat.terminate()
