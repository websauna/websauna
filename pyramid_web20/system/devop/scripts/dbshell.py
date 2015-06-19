"""Run pgcli shell on the configured database."""
import os
import sys
from pyramid.paster import bootstrap

from pyramid_web20.utils.configincluder import monkey_patch_paster_config_parser
from pyramid.paster import setup_logging
from pyramid.scripts.common import parse_vars


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
    options = parse_vars(argv[2:])
    setup_logging(config_uri)

    bootstrap_env = bootstrap(config_uri, options=dict(sanity_check=False))
    url = bootstrap_env["registry"].settings.get("sqlalchemy.url")

    os.system("pgcli {}".format(url))