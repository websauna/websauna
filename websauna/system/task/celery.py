"""Wrap pyramid_celery loader, so that it works with our INI includer hack."""

from websauna.utils.configincluder import IncludeAwareConfigParser
from websauna.utils.configincluder import monkey_patch_paster_config_parser

monkey_patch_paster_config_parser()

from pyramid_celery.loaders import INILoader
INILoader.ConfigParser = IncludeAwareConfigParser

# TODO: replace pyramid_celery with some more decoupled implementatin
from pyramid_celery import celery_app
from pyramid_celery import includeme


# Export pyramid_celery as pass through
__all__ = ["celery_app", "includeme"]

