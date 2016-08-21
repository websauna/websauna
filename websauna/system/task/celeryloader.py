"""Celery process."""
import os

try:
    # Could not find way around this :(
    # Make Celery play nice if gevent is used
    # http://stackoverflow.com/a/30707837/315168
    import gevent
    from gevent import monkey

    print("Warning! Running in implicit gevent monkey patch")
    monkey.patch_all()

    # import redis
    # import redis.connection
    # redis.connection.socket = gevent.socket
except ImportError:
    pass

import sys

from celery.loaders.base import BaseLoader
from pyramid.decorator import reify
from websauna.system.devop.cmdline import init_websauna
from websauna.system.http import Request

from .celery import get_celery_config


ini_file = None


class WebsaunaLoader(BaseLoader):
    """Celery command line loader for Websauna.

    Support binding request object to Celery tasks and loading Celery settings through Pyramid INI configuration.
    """

    @reify
    def request(self) -> Request:
        """Bootstrap WSGI environment with request object and such."""
        request = init_websauna(ini_file)
        return request

    def read_configuration(self) -> dict:
        """Load Celery config from Pyramid INI file."""
        config = get_celery_config(self.request.registry)
        return config

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

        Pass our request context to the task.

        http://docs.celeryproject.org/en/latest/userguide/tasks.html#context

        .. note ::

            The same request object is recycled over and over again. Pyramid does not have correctly mechanisms for having retryable request factory.

        """
        task.request.update(request=self.request)


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

    # https://github.com/celery/celery/issues/3405
    os.environ["CELERY_LOADER"]  = "websauna.system.task.celeryloader.WebsaunaLoader"
    argv = ["celery"] + celery_args
    # Directly jump to Celery 4.0+ entry point
    from celery.bin.celery import main
    main(argv)


