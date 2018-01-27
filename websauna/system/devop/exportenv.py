"""Export settings and secrets as environment variables to subprocesses."""
# Standard Library
import os

# Pyramid
from pyramid.registry import Registry

# SQLAlchemy
from sqlalchemy.engine.url import make_url

# Websauna
from websauna.system.core.utils import get_secrets


def create_settings_env(registry: Registry):
    """Create os.environ where have exported all settings and secrets.

    This is used for subprocess to create a child processes which are aware of our settings.  All dots are replaced with underscores. The exported environment varible is either prefixed with ``main``  or ``secret``. The exported environment variables are uppercased. Parent process environment variables are automatically inherited.

    The environment will look like::

        MAIN_websauna_SITE_ID=foo
        SECRETS_AWS_CONSUMER_KEY=baa

    You will also have::

        MAIN_SQL_HOST
        MAIN_SQL_DATABASE
        MAIN_SQL_USER
        MAIN_SQL_PASSWORD

    Integers, booleans and objects are exported as strings:

        MAIN_SOME_BOOLEAN=True
        MAIN_SOME_INTEGER=123

    """
    env = os.environ.copy()

    settings = registry.settings
    secrets = get_secrets(registry)

    # Export database credentials
    url = make_url(settings["sqlalchemy.url"])

    env["MAIN_SQL_HOST"] = url.host or ""
    env["MAIN_SQL_DATABASE"] = url.database or ""
    env["MAIN_SQL_USERNAME"] = url.username or ""
    env["MAIN_SQL_PASSWORD"] = url.password or ""

    for key, val in settings.items():
        key = "main.{}".format(key)
        key = key.replace(".", "_")
        env[key.upper()] = str(val)

    for key, val in secrets.items():
        key = "secret.{k}".format(k=key)
        key = key.replace(".", "_")
        env[key.upper()] = str(val)

    return env
