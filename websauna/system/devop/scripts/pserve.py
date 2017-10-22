"""Config file includer aware wrapper for pserve."""
import os
import sys
from pkg_resources import load_entry_point

from websauna.system.devop.cmdline import prepare_config_uri

try:
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    pass


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
    sys.exit(
        load_entry_point('pyramid', 'console_scripts', 'pserve')()
    )
