"""Helper functions to initializer Websauna framework for command line applications."""
import logging
import os
from logging.config import fileConfig
import sys

from pyramid import scripting
from pyramid.paster import bootstrap
from websauna.utils.configincluder import _getpathsec
from websauna.system.http.utils import make_routable_request
from websauna.system.model.meta import create_dbsession

from rainbow_logging_handler import RainbowLoggingHandler

from websauna.system.http import Request


def setup_logging(config_uri, disable_existing_loggers=False):
    """Include-aware Python logging setup from INI config file.
    """
    path, _ = _getpathsec(config_uri, None)
    parser = IncludeAwareConfigParser()
    parser.read([path])

    if parser.has_section('loggers'):
        config_file = os.path.abspath(path)
        defaults = dict(parser, here=os.path.dirname(config_file))
        return fileConfig(parser, defaults, disable_existing_loggers)


def setup_console_logging(log_level=None):
    """Setup console logging.

    Aimed to give easy sane defaults for loggig in command line applications.

    Don't use logging settings from INI, but use hardcoded defaults.
    """

    formatter = logging.Formatter("[%(asctime)s] [%(name)s %(funcName)s] %(message)s")  # same as default

    # setup `RainbowLoggingHandler`
    # and quiet some logs for the test output
    handler = RainbowLoggingHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.handlers = [handler]

    env_level = os.environ.get("LOG_LEVEL", "info")
    log_level = log_level or getattr(logging, env_level.upper())
    logger.setLevel(log_level)

    logger = logging.getLogger("requests.packages.urllib3.connectionpool")
    logger.setLevel(logging.ERROR)

    # SQL Alchemy transactions
    logger = logging.getLogger("txn")
    logger.setLevel(logging.ERROR)


def init_websauna(config_uri: str, sanity_check: bool=False, console_app=False, extra_options=None) -> Request:
    """Initialize Websauna WSGI application for a command line oriented script.

    Example:

    .. code-block:: python

        import sys
        from websauna.system.devop.cmdline import init_websauna

        config_uri = sys.argv[1]
        request = init_websauna(config_uri)

    :param config_uri: Path to config INI file

    :param sanity_check: Perform database sanity check on start

    :param console_app: Set true to setup console-mode logging. See :func:`setup_console_logging`

    :param extra_options: Passed through bootstrap() and is available as :attr:`websauna.system.Initializer.global_options`.

    :return: Faux Request object pointing to a site root, having registry and every configured.
    """

    # Paster thinks we are a string
    if sanity_check:
        sanity_check = "true"
    else:
        sanity_check = "false"

    options = {
        "sanity_check": sanity_check
    }

    if extra_options:
        options.update(extra_options)

    bootstrap_env = bootstrap(config_uri, options=options)
    app = bootstrap_env["app"]
    initializer = getattr(app, "initializer", None)
    assert initializer is not None, "Configuration did not yield to Websauna application with Initializer set up"

    registry = initializer.config.registry
    dbsession = create_dbsession(registry)

    # Set up the request with websauna.site_url setting as the base URL
    request = make_routable_request(dbsession, registry)

    # This exposes the app object for the integration tests e.g test_static_asset
    # TODO: Find a cleaner way to do this
    request.app = app

    return request


def init_websauna_script_env(config_uri: str) -> dict:
    """Initialize Websauna WSGI application for a IPython notebook.

    :param config_uri: Path to config INI file

    :return: Dictionary of shell variables
    """

    bootstrap_env = bootstrap(config_uri, options=dict(sanity_check=False))
    app = bootstrap_env["app"]
    initializer = getattr(app, "initializer", None)
    assert initializer is not None, "Configuration did not yield to Websauna application with Initializer set up"

    registry = initializer.config.registry
    dbsession = create_dbsession(registry)

    pyramid_env = scripting.prepare(registry=app.initializer.config.registry)
    pyramid_env["app"] = app
    pyramid_env["initializer"] = initializer

    # Websauna specific
    # Set up the request with websauna.site_url setting as the base URL
    request = make_routable_request(dbsession, registry)
    pyramid_env["request"] = request
    pyramid_env["dbsession"] = dbsession

    return pyramid_env
