"""ws-collect-static script.

Read through all configured static views and compile their assets to ``collected-static`` folder.
"""
# Standard Library
import sys
import typing as t

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.scripts import feedback_and_exit
from websauna.system.devop.scripts import get_config_uri
from websauna.system.devop.scripts import usage_message


def main(argv: t.List[str]=sys.argv):
    """Read through all configured static views and compile their assets to ``collected-static`` folder.

    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    if len(argv) < 2:
        usage_message(argv)

    config_uri = get_config_uri(argv)
    request = init_websauna(config_uri, sanity_check=False)
    request.registry.static_asset_policy.collect_static()
    feedback_and_exit('ws-collect-static: Collected all static assets', 0, True)
