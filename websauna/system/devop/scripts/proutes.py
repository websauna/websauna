"""ws-proutes script.

DEPRECATED: Wrapper around Pyramid proutes script.
"""
# Standard Library
import sys
import typing as t

# Websauna
from websauna.system.devop.scripts import proxy_to_pyramid_script


def main(argv: t.List[str]=sys.argv):
    """Proxy to Pyramid proutes script.

    This script is deprecated and will be removed in Websauna 1.0.0
    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    proxy_to_pyramid_script('proutes', argv)
