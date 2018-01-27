"""ws-sanity-check script.

Execute a sanity check on the configuration.
"""
# Standard Library
import sys
import typing as t

# Websauna
from websauna.system import SanityCheckFailed
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.scripts import FAIL_MSG
from websauna.system.devop.scripts import feedback_and_exit
from websauna.system.devop.scripts import get_config_uri
from websauna.system.devop.scripts import usage_message


SUCCESS_MSG = """Sanity check passed"""

NOT_FOUND_MSG = """
Sanity check failed

Reason:
Config {config_uri} was not found.
"""


def main(argv: t.List[str]=sys.argv):
    """Execute a sanity check on the configuration.

    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    if len(argv) < 2:
        usage_message(argv)

    config_uri = get_config_uri(argv)

    try:
        init_websauna(config_uri, sanity_check=True)
    except SanityCheckFailed as exc:
        feedback_and_exit(FAIL_MSG.format(exception=str(exc)), 10)
    except FileNotFoundError as exc:
        feedback_and_exit(NOT_FOUND_MSG.format(config_uri=config_uri), 10)

    feedback_and_exit(SUCCESS_MSG, 0)
