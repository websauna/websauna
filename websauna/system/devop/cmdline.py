"""Helper functions to initializer Websauna framework for command line applications."""
import os
from logging.config import fileConfig

from pyramid import scripting
from pyramid.paster import bootstrap, setup_logging, _getpathsec
from websauna.system.http import Request
from websauna.utils.configincluder import monkey_patch_paster_config_parser, IncludeAwareConfigParser


def setup_logging(config_uri):
    """Include-aware Python logging setup from INI config file.
    """
    path, _ = _getpathsec(config_uri, None)
    parser = IncludeAwareConfigParser()
    parser.read([path])

    if parser.has_section('loggers'):
        config_file = os.path.abspath(path)
        defaults = dict(parser, here=os.path.dirname(config_file))
        return fileConfig(parser, defaults)


def init_websauna(config_uri: str, sanity_check=False) -> Request:
    """Initialize Websauna WSGI application for a command line oriented script.

    :param config_uri: Path to config INI file

    :param sanity_check: Perform database sanity check on start

    :return: Dummy request object pointing to a site root, having registry and every configured.
    """

    monkey_patch_paster_config_parser()

    setup_logging(config_uri)

    bootstrap_env = bootstrap(config_uri, options=dict(sanity_check=sanity_check))
    app = bootstrap_env["app"]
    initializer = getattr(app, "initializer", None)
    assert initializer is not None, "Configuration did not yield to Websauna application with Initializer set up"

    pyramid_env = scripting.prepare(registry=app.initializer.config.registry)
    request = pyramid_env["request"]

    # Export application object for testing
    request.app = app

    return pyramid_env["request"]

