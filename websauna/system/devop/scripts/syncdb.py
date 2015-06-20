import os
import sys
from pyramid.paster import bootstrap

from websauna.utils.configincluder import monkey_patch_paster_config_parser

monkey_patch_paster_config_parser()

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars
from websauna.system import get_init
from websauna.system.model import DBSession
from websauna.system.model import Base


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

    bootstrap(config_uri, options=dict(sanity_check=False))

    engine = DBSession.get_bind()
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()