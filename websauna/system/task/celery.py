"""Wrap pyramid_celery loader, so that it works with our INI includer hack."""
import textwrap

import venusian
from celery import Celery

from pyramid.registry import Registry

_command_line_request = None


def get_celery_config(registry) -> dict:
    """Load Celery configuration from settings.

    You need to have a setting key ``celery_config_python``. This is Python code to configure Celery. The code is executed and all locals are passed to Celery app.

    More information

    * http://docs.celeryproject.org/en/master/userguide/configuration.html

    :param registry: Pyramid registry from where we read the Celery configuratino

    :return: An object holding Celery configuration variables
    """

    celery_config_python = registry.settings.get("celery_config_python")
    if not celery_config_python:
        raise RuntimeError("Using Celery with Websauna requires you to have celery_config_python configuration variable")

    # Expose timedelta object for config to be used in beat schedule
    # http://docs.celeryproject.org/en/master/userguide/periodic-tasks.html#beat-entries
    from datetime import timedelta  # noqa

    _globals = globals().copy()
    _locals = locals().copy()
    code = textwrap.dedent(celery_config_python)

    try:
        config_dict = eval(code, _globals, _locals)
    except Exception as e:
        raise RuntimeError("Could not execute Python code to produce Celery configuration object: {}".format(code)) from e

    if "broker_url" not in config_dict:
        raise RuntimeError("Mandatory broker_url Celery setting missing. Did we fail to parse config? {}".format(config_dict))

    return config_dict


def get_celery(registry: Registry):
    """Load and configure Celery app.

    Cache Celery root object on registry.

    :param registry:
    :return:
    """
    celery = getattr(registry, "celery", None)
    if not celery:
        celery = registry.celery = Celery()
        celery.conf.update(get_celery_config(registry))

    return celery


def task(*args, **kwargs):
    """Pyramid configuration compatible task definer.

    Tasks are not picked up until you run :py:meth:`pyramid.config.Configurator.scan` on the module.
    Otherwise we follow the behavior of :py:meth:`celery.Celery.task`.

    :param args: Passed to Celery task decorator
    :param kwargs: Passed to Celery task decorator
    """


    def _inner(func):
        "The class decorator example"

        def register(scanner, name, wrapped):
            config = scanner.config
            registry = config.registry

            tasks = getattr(registry, "celery_tasks", None)
            if not tasks:
                tasks = registry.celery_tasks = []

            # Have Celery tasks registered to a list hold in the registry
            # so register_tasks() can read them from there when
            # Celery worker is ready
            tasks.append((func, args, kwargs))

        venusian.attach(func, register, category='celery')
        return func

    return _inner






