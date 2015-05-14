"""Export settings and secrets as environment variables to subprocesses."""

import os
from pyramid_web20.system.core.secrets import get_secrets


def create_settings_env(registry):
    """Create os.environ where have exported all settings and secrets.

    This is used for subprocess to create a child processes which are aware of our settings.  All dots are replaced with underscores. The exported environment varible is either prefixed with ``main``  or ``secret`. The exported environment variables are uppercased. Parent process environment variables are automatically inherited.

    The environment will look like::

        MAIN_PYRAMID_WEB20_SITE_ID=foo
        SECRETS_AWS_CONSUMER_KEY=baa

    Integers, booleans and objects are exported as strings:

        MAIN_SOME_BOOLEAN=True
        MAIN_SOME_INTEGER=123

    """
    env = os.environ.copy()

    settings = registry.settings
    secrets = get_secrets(registry)

    for key, val in settings.items():
        key = "main.{}".format(key)
        key = key.replace(".", "_")
        env[key.upper()] = str(val)

    for key, val in secrets.items():
        key = "secret.{}".format(key)
        key = key.replace(".", "_")
        env[key.upper()] = str(val)

    return env
