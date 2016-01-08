"""Run pgcli shell on the configured database."""
import os
import sys

from websauna.system.devop.cmdline import init_websauna
from websauna.utils.configincluder import monkey_patch_paster_config_parser


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    monkey_patch_paster_config_parser()

    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]

    # Print out the connection URL with the password masked out
    request = init_websauna(config_uri)
    url = request.registry.settings.get("sqlalchemy.url")

    engine = request.dbsession.get_bind()
    print("Connecting to {}".format(engine))

    os.system("pgcli {}".format(url))