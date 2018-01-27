"""INI-file based secrets reading."""
# Standard Library
import configparser
import io
import os
from urllib.parse import urlparse

import pkg_resources


_resource_manager = pkg_resources.ResourceManager()


class MissingSecretsEnvironmentVariable(Exception):
    """Thrown when we try to interpolate an environment variable that does not exist."""


def resolve(uri):
    """Resolve secrets location."""

    # Do we look like a relative file (no URL scheme)
    if "://" not in uri:
        uri = "file://" + os.path.abspath(os.path.join(os.getcwd(), uri))

    parts = urlparse(uri)

    assert parts.scheme in ("resource", "file"), "Only resource//: scheme supported, got {}".format(uri)

    if parts.scheme == "resource":
        package = parts.netloc
        args = package.split('.') + [parts.path.lstrip('/')]
        path = os.path.join(*args)

        req = pkg_resources.Requirement.parse(package)
        assert _resource_manager.resource_exists(req, path), "Could not find {}".format(uri)

        config_source = _resource_manager.resource_stream(req, path)
    else:
        config_source = io.open(parts.path, "rb")

    return config_source


def read_ini_secrets(secrets_file, strict=True) -> dict:
    """Read plaintext .INI file to pick up secrets.

    Dummy secrets handler which does not have encryption. Reads INI file. Creates dictionary keys in format [ini section name].[ini key name] = value. Entries with a leading $ are environment variable expansions.

    Example INI contents::

        [authentication]
        secret = CHANGEME

        [authomatic]
        # This is a secret seed used in various OAuth related keys
        secret = CHANGEME

        [facebook]
        consumer_key = $FACEBOOK_CONSUMER_KEY
        consumer_secret = $FACEBOOK_CONSUMER_SECRET

    The following ``secrets_file`` formats are supported

    * A path relative to the current working directory, e.g. ``test-secrets.ini``

    * Absolute path using ``file://`` URL: ``file:///etc/myproject/mysecrets.ini``

    * A path relative to deployed Python package. E.g. ``resource://websauna/conf/test-settings.ini``

    :param secrets_file: URI like ``resource://websauna/conf/test-settings.ini``

    :param strict: Bail out in the environment variable expansion if the environment variable is not. Useful e.g. for testing when all users are not assumed to know all secrets. In non-strict mode if the environment variable is missing the secret value is set to ``None``.

    :return: ``ConfigParser`` instance.

    """
    secrets = {}

    fp = resolve(secrets_file)
    text = fp.read().decode("utf-8")

    secrets_config = configparser.ConfigParser()
    secrets_config.read_string(text, source=secrets_file)

    for section in secrets_config.sections():
        for key, value in secrets_config.items(section):

            if value.startswith("$"):
                environment_variable = value[1:]
                value = os.getenv(environment_variable, None)
                if not value and strict:
                    raise MissingSecretsEnvironmentVariable("Secrets key {} needs environment variable {} in file {} section {}".format(key, environment_variable, secrets_file, section))

            secrets["{}.{}".format(section, key)] = value

    return secrets
