import os
import sys

from pyramid.scripts import ptweens

from websauna.system.devop.cmdline import prepare_config_uri


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s conf/production.ini")' % (cmd, cmd))
    sys.exit(1)


def main():
    argv = sys.argv
    if len(argv) < 2:
        usage(argv)
    argv[1] = prepare_config_uri(argv[1])
    sys.exit(ptweens.main() or 0)
