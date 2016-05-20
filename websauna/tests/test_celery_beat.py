"""See that scheduled tasks are run by Celery beat."""

import subprocess
import time
import os

from flaky import flaky

from websauna.system.core.redis import get_redis


def run_worker_and_beat(ini_file):

    cmdline = ["ws-celery", "worker", "-A", "websauna.system.task.celery.celery_app", "--ini", ini_file]

    # You can start manually ws-celery worker -A websauna.system.task.celery.celery_app --ini websauna/tests/scheduler-test.ini
    # # and set worker = None

    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2.0)

    worker.poll()
    if worker.returncode is not None:
         raise AssertionError("Scheduler process did not start up: {}".format(" ".join(cmdline)))

    # You can run manually ws-celery beat -A websauna.system.task.celery.celery_app --ini websauna/tests/scheduler-test.ini
    cmdline = ["ws-celery", "beat", "-A", "websauna.system.task.celery.celery_app", "--ini", ini_file]
    beat = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(1.0)
    beat.poll()
    if beat.returncode is not None:
        worker.terminate()
        AssertionError("Beat process did not start up")

    return worker, beat


@flaky
def test_run_scheduled(init):
    """Scheduled tasks run properly on the celery worker + celery beat process."""

    ini_file = os.path.join(os.path.dirname(__file__), "scheduler-test.ini")
    worker, beat = run_worker_and_beat(ini_file)
    # worker, beat = None, None

    try:
        # Reset test database
        redis = get_redis(init.config.registry)
        redis.delete("foo", "bar")

        # scheduledtasks.ticker should beat every second and reset values in Redis
        # sets foo
        time.sleep(10)

        redis = get_redis(init.config.registry)
        foo = redis.get("foo")

        if worker:
            assert worker.returncode is None

        if beat:
            assert beat.returncode is None

        assert foo == b"foo"  # Set back by its original value by 1 second beat

    finally:
        try:
            worker and worker.terminate()
        except ProcessLookupError:
            pass

        try:
            beat and beat.terminate()
        except ProcessLookupError:
            pass
