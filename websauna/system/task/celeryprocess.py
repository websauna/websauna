"""Celery process."""
import sys

from celery.loaders.base import BaseLoader
from pyramid.decorator import reify
from pyramid.scripting import _make_request
from websauna.system.devop.cmdline import init_websauna
from websauna.system.http import Request

from .celery import get_celery_config


ini_file = None


class WebsaunaLoader(BaseLoader):
    """Celery command line loader for Websauna.

    Support binding request object to Celery tasks and loading Celery settings through Pyramid INI configuration.

    TODO: We do not call any closer method for the request ATM
    """

    @reify
    def request(self) -> Request:
        """Bootstrap WSGI environment with request object and such."""
        request = init_websauna(ini_file)
        return request

    def read_configuration(self) -> dict:
        """Load Celery config from Pyramid INI file."""
        return get_celery_config(self.request.registry)

    def import_task_module(self, module):
        raise RuntimeError("imports Celery config directive is not supported. Use config.scan() to pick up tasks.")

    def register_tasks(self):
        """Inform Celery of all tasks registered through our Venusian-compatible task decorator."""

        # @task() decorator pick ups
        tasks = getattr(self.request.registry, "celery_tasks", [])

        for func, args, kwargs in tasks:
            decorator_args = [func] + list(args)
            self.app.task(*decorator_args, **kwargs)

    def on_worker_init(self):
        """This method is called when a child process starts."""

        #: Associate this process as Celery app object of the environment
        self.request.registry.celery = self.app

        #: Associate request for celery app, so
        #: task executor knows about Request object
        self.app.request = self.request

        self.register_tasks()

    def on_task_init(self, task_id, task):
        """This method is called before a task is executed.

        Pass our request context to the task

        http://docs.celeryproject.org/en/latest/userguide/tasks.html#context
        """

        # We don't want to recycle request object across tasks, as
        # all reifyed attributes would stay stale and such.
        request = self.request
        new_request = _make_request("/", request.registry)

        # Pass freshly created request in task function context
        task.request.update(request=new_request)


def main():
    """Celery process entry point.

    Wrap celery command line script with our INI reader.

    .. note ::

        Make sure there is no global app = Celery() in any point of your code base,
        or this doesn't work.

    """
    global ini_file

    if len(sys.argv) < 2:
        sys.exit("Example usage: ws-celery myapp/conf/development.ini -- worker")

    ini_file = sys.argv[1]
    if not ini_file.endswith(".ini"):
        sys.exit("The first argument must be a configuration file")

    if len(sys.argv) >= 3:
        if not sys.argv[2] == "--":
            raise RuntimeError("The second argument must be -- to signal command line argument passthrough")
        celery_args = sys.argv[3:]
    else:
        celery_args = []

    argv = ["--loader=websauna.system.task.celeryprocess.WebsaunaLoader"] + celery_args

    # Directly jump to Celery 4.0+ entry point
    from celery.bin.celery import main
    print("Running celery as ", argv)

    main(argv)