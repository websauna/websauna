from pyramid import scripting
from pyramid.paster import bootstrap
from websauna.system.http import Request


def init_websauna(config_uri) -> Request:
    """Initialize Websauna WSGI application for a command line oriented script."""

    bootstrap_env = bootstrap(config_uri, options=dict(sanity_check=False))
    app = bootstrap_env["app"]
    initializer = getattr(app, "initializer", None)
    assert initializer is not None, "Configuration did not yield to Websauna application with Initializer set up"

    pyramid_env = scripting.prepare(registry=app.initializer.config.registry)

    return pyramid_env["request"]

