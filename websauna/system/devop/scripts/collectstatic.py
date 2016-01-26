"""ws-collect-static script."""
import getpass

import os
import sys

from websauna.system import SanityCheckFailed
from websauna.system.devop.cmdline import init_websauna


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s conf/production.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):

    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    request = init_websauna(config_uri, sanity_check=False)
    request.registry.static_asset_policy.collect_static()
    sys.exit(0)
