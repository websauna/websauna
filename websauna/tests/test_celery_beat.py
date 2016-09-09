"""See that beat runs scheduled tasks correctly."""

import subprocess
import time
import os

from flaky import flaky

from websauna.system.core.redis import get_redis


def run_worker_and_beat(ini_file):

    cmdline = "ws-celery {} -- worker --loglevel=debug".format(ini_file)

    # You can start manually ws-celery worker -A websauna.system.task.celery.celery_app --ini websauna/tests/scheduler-test.ini
    # # and set worker = None

    worker = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    time.sleep(2.0)

    worker.poll()
    if worker.returncode is not None:
        print(worker.stdout.read().decode("utf-8"))
        print(worker.stderr.read().decode("utf-8"))
        raise AssertionError("Celery worker process did not start up: {}".format(cmdline))

    # You can run manually ws-celery beat -A websauna.system.task.celery.celery_app --ini websauna/tests/scheduler-test.ini
    cmdline = "ws-celery {} -- beat".format(ini_file)
    beat = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    time.sleep(1.0)
    beat.poll()
    if beat.returncode is not None:
        worker.terminate()
        AssertionError("Beat process did not start up")

    return worker, beat


@flaky
def test_celery_beat(init):
    """Scheduled tasks run properly on the celery worker + celery beat process."""

    ini_file = os.path.join(os.path.dirname(__file__), "task-test.ini")
    worker, beat = run_worker_and_beat(ini_file)

    try:
        # Reset test database
        redis = get_redis(init.config.registry)
        redis.delete("foo", "bar")

        # scheduledtasks.ticker should beat every second and reset values in Redis
        # sets foo
        time.sleep(5)

        redis = get_redis(init.config.registry)
        foo = redis.get("foo")

        if worker:
            assert worker.returncode is None

        if beat:
            assert beat.returncode is None

        assert foo == b"xoo"  # Set back by its original value by 1 second beat

    finally:
        try:
            worker and worker.terminate()
            print(worker.stdout.read().decode("utf-8"))
        except ProcessLookupError:
            pass

        try:
            beat and beat.terminate()
            print(beat.stdout.read().decode("utf-8"))
        except ProcessLookupError:
            pass
