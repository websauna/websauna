"""ws-pserve script.

DEPRECATED: Wrapper around Pyramid pserve script.
"""
# Standard Library
import sys
import typing as t

# Websauna
from websauna.system.devop.scripts import proxy_to_pyramid_script


try:
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    pass


def main(argv: t.List[str]=sys.argv):
    """Proxy to Pyramid pserve script.

    This script is deprecated and will be removed in Websauna 1.0.0
    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    proxy_to_pyramid_script('pserve', argv)
