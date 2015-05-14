import configparser
import os
from zope.interface import Interface


class ISecrets(Interface):
    """Utility marker interface which gives us our secrets.

    Secrets is a dictionary which hold sensitive deployment data.
    """


def get_secrets(registry):
    """Get the secrets provider dictionary."""
    return registry.getUtility(ISecrets)


def read_init_secrets(secrets_file):
    """Read plaintext .ini file to pick up secrets.

    Dummy secrets handler which does not have encryption. Reads INI file. Creates dictionary keys in format [ini section name].[ini key name] = value.
    """
    secrets = {}

    if not os.path.exists(secrets_file):
        p = os.path.abspath(secrets_file)
        raise RuntimeError("Secrets file {} missing".format(p))

    secrets_config = configparser.ConfigParser()
    secrets_config.read(secrets_file)

    for section in secrets_config.sections():
        for key, value in secrets_config.items(section):
            secrets["{}.{}".format(section, key)] = value

    return secrets
