"""See that beat runs scheduled tasks correctly."""

# Standard Library
import subprocess
import time

from flaky import flaky

# Websauna
from websauna.system.core.redis import get_redis


def run_worker_and_beat(ini_file):

    cmdline = "ws-celery ws://{} -- worker --loglevel=debug".format(ini_file)

    # You can start manually ws-celery websauna/tests/task-test.ini -- worker --loglevel=debug
    # and set worker = False
    worker = None

    if worker is None:
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
        if worker:
            worker.terminate()
            AssertionError("Beat process did not start up")

    return worker, beat


@flaky
def test_celery_beat(init):
    """Scheduled tasks run properly on the celery worker + celery beat process."""

    ini_file = 'websauna/tests/task/task-test.ini'
    worker, beat = run_worker_and_beat(ini_file)

    try:
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

        if worker:
            assert worker.returncode is None

        if beat:
            assert beat.returncode is None

        if foo != b"xoo":
            # TravisCI headless debugging
            # print(worker.stdout.read().decode("utf-8"))
            # print(worker.stderr.read().decode("utf-8"))
            # print(beat.stdout.read().decode("utf-8"))
            # print(beat.stderr.read().decode("utf-8"))
            pass

        assert foo == b"xoo"  # Set back by its original value by 1 second beat

    finally:
        try:
            if worker:
                worker.terminate()
        except ProcessLookupError:
            pass

        try:
            beat and beat.terminate()
        except ProcessLookupError:
            pass
