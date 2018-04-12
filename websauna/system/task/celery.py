"""Get Celery instance from Pyramid configuration."""
# Standard Library
import textwrap

# Pyramid
from pyramid.registry import Registry

# Celery
from celery import Celery


def parse_celery_config(celery_config_python: str, *, settings) -> dict:
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


def get_celery_config(registry: Registry) -> dict:
    """Load Celery configuration from settings.

    You need to have a setting key ``celery_config_python``. This is Python code to configure Celery. The code is executed and all locals are passed to Celery app.

    More information:

        * http://docs.celeryproject.org/en/master/userguide/configuration.html

    :param registry: Pyramid registry from where we read the Celery configuratino
    :return: An object holding Celery configuration variables
    """

    celery_config_python = registry.settings.get("websauna.celery_config")
    if not celery_config_python:
        raise RuntimeError('Using Celery with Websauna requires you to have celery_config_python configuration variable')

    return parse_celery_config(celery_config_python, settings=registry.settings)


def get_celery(registry: Registry):
    """Load and configure Celery app.

    Cache the loaded Celery app object on registry.

    :param registry: Use registry settings to load Celery
    """
    celery = getattr(registry, "celery", None)
    if not celery:
        celery = registry.celery = Celery()
        celery.conf.update(get_celery_config(registry))

        # Expose Pyramid registry to Celery app and tasks
        celery.registry = registry

    return celery
