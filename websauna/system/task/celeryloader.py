"""Celery process."""
# Standard Library
import logging
import os
import sys
import typing as t

# Pyramid
import plaster

from celery.loaders.base import BaseLoader
from celery.signals import setup_logging as _setup_logging_signal

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.cmdline import setup_logging
from websauna.system.devop.scripts import feedback_and_exit
from websauna.system.devop.scripts import get_config_uri
from websauna.system.http.utils import make_routable_request
from websauna.system.model.retry import ensure_transactionless
from websauna.system.task.celery import parse_celery_config
from websauna.utils.secrets import read_ini_secrets


logger = logging.getLogger(__name__)


#: Passed through Celery loader mechanism
ini_file = ''


def usage_message(argv: t.List[str]):
    """Display usage message and exit.

    :param argv: Command line arguments.
    :raises sys.SystemExit:
    """
    cmd = os.path.basename(argv[0])
    msg = (
        'usage: {cmd} <config_uri> -- worker\n'
        '(example: "{cmd} ws://conf/production.ini -- worker")'
    ).format(cmd=cmd)
    feedback_and_exit(msg, status_code=1, display_border=False)


class WebsaunaLoader(BaseLoader):
    """Celery command line loader for Websauna.

    Support binding request object to Celery tasks and loading Celery settings through Pyramid INI configuration.
    """

    def get_celery_config(self, settings) -> str:
        """Return celery configuration from Websauna (optionally secret-) settings.

        :param settings: Websauna settings (from app:main section).
        :return: Celery configuration, as a string.
        """
        value = None
        secrets_file = settings.get('websauna.secrets_file')
        if secrets_file:
            secrets = read_ini_secrets(secrets_file)
            value = secrets.get('app:main.websauna.celery_config', '')
        value = value or settings.get('websauna.celery_config')
        if not value:
            raise RuntimeError('No Celery configuration found in settings')
        return value

    def read_configuration(self, **kwargs) -> dict:
        """BaseLoader API override to load Celery config from Pyramid INI file.

        We need to be able to do this without ramping up full Websauna,
        because that's the order of the events Celery worker wants.
        This way we avoid circular dependencies during Celery worker start up.
        """
        loader = plaster.get_loader(ini_file)  # global
        settings = loader.get_settings('app:main')

        try:
            value = self.get_celery_config(settings)
        except RuntimeError as exc:
            raise RuntimeError('Bad or missing Celery configuration in "%s": %s' % (ini_file, exc))

        config = parse_celery_config(value, settings=settings)
        return config

    def import_task_module(self, module):
        raise RuntimeError('Import Celery config directive is not supported. Use config.scan() to pick up tasks.')

    def register_tasks(self):
        """Inform Celery of all tasks registered through our Venusian-compatible task decorator."""
        # @task() decorator pick ups
        tasks = getattr(self.request.registry, "celery_tasks", [])

        for func, args, kwargs in tasks:
            decorator_args = [func] + list(args)
            self.app.task(*decorator_args, **kwargs)

    def _set_request(self):
        """Set a request for WebsaunaLoader."""
        # TODO Make sanity_check True by default,
        # but make it sure we can disable it in tests,
        # because otherwise tests won't run
        self.request = init_websauna(ini_file, sanity_check=False)

        #: Associate this process as Celery app object of the environment
        self.request.registry.celery = self.app

        #: Associate request for celery app, so
        #: task executor knows about Request object
        self.app.cmdline_request = self.request

    def on_worker_init(self):
        """This method is called when a child process starts."""
        self._set_request()
        self.register_tasks()

    def on_task_init(self, task_id, task):
        """This method is called before a task is executed.

        Pass our request context to the task.

        http://docs.celeryproject.org/en/latest/userguide/tasks.html#context

        .. note ::

            The same request object is recycled over and over again. Pyramid does not have correctly mechanisms for having retryable request factory.

        """

        # TODO: How Celery handles retries?

        # We must not have on-going transaction when worker spawns a task
        # - otherwise it means init code has left transaction open
        ensure_transactionless("Thread local TX was ongoing when Celery fired up a new task {}: {}".format(task_id, task))

        # When using celery groups, the request is not available, we set it here.
        if not hasattr(self, 'request'):
            self._set_request()

        # Each tasks gets a new request with its own transaction manager and dbsession
        request = make_routable_request(dbsession=None, registry=self.request.registry)

        task.request.update(request=request)


@_setup_logging_signal.connect
def fix_celery_logging(loglevel, logfile, format, colorize, **kwargs):
    """Fix Celery logging by re-enforcing our loggers after Celery messes up them."""
    setup_logging(ini_file)


def main(argv: t.List[str]=sys.argv):
    """Celery process entry point.

    Wrap celery command line script with our INI reader.

    .. note ::

        Make sure there is no global app = Celery() in any point of your code base,
        or this doesn't work.

    """
    global ini_file
    global request

    if len(argv) < 2:
        usage_message(argv)

    ini_file = get_config_uri(argv)
    if not ini_file.endswith(".ini"):
        sys.exit("The first argument must be a configuration file")

    if len(argv) >= 3:
        if not argv[2] == "--":
            raise RuntimeError("The second argument must be -- to signal command line argument passthrough")
        celery_args = sys.argv[3:]
    else:
        celery_args = []

    # https://github.com/celery/celery/issues/3405
    os.environ["CELERY_LOADER"] = "websauna.system.task.celeryloader.WebsaunaLoader"
    argv = ["celery"] + celery_args
    # Directly jump to Celery 4.0+ entry point
    from celery.bin.celery import main
    main(argv)
