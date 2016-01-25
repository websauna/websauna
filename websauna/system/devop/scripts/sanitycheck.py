"""ws-sanity-check script."""
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
    try:
        request = init_websauna(config_uri, sanity_check=True)
    except SanityCheckFailed:
        print("It did not go that well.")
        sys.exit(10)

    print("All good.")
    sys.exit(0)
