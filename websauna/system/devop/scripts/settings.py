"""ws-settings script.


Display settings for a given configuration file.
"""
# Standard Library
import sys
import typing as t
from pprint import pprint

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.scripts import feedback
from websauna.system.devop.scripts import feedback_and_exit
from websauna.system.devop.scripts import get_config_uri
from websauna.system.devop.scripts import usage_message


def main(argv: t.List[str]=sys.argv):
    """Display settings for a given configuration file.

    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    if len(argv) < 2:
        usage_message(argv)

    config_uri = get_config_uri(argv)

    request = init_websauna(config_uri, sanity_check=False)
    message = 'Active deployment settings in {config_uri}'.format(config_uri=config_uri)
    feedback(message)
    pprint(request.registry.settings)
    feedback_and_exit('', status_code=0, display_border=True)
