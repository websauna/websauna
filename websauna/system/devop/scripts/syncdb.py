import os
import sys

import transaction
from websauna.utils.configincluder import monkey_patch_paster_config_parser
from websauna.system.devop.cmdline import init_websauna
from websauna.system.model.meta import Base

monkey_patch_paster_config_parser()

from pyramid.paster import setup_logging

from pyramid.scripts.common import parse_vars


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [ARG1, ARG2...] \n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):

    monkey_patch_paster_config_parser()

    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)

    request = init_websauna(config_uri)
    with transaction.manager:
        engine = request.dbsession.get_bind()
        Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()