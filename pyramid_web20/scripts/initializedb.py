import os
import sys

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars
from pyramid_web20 import get_init
from pyramid_web20.models import DBSession
from pyramid_web20.models import Base


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)

    settings = get_appsettings(config_uri, options=options)

    init = get_init(settings)

    # secrets = init.read_secrets(settings)
    # This must go first, as we need to make sure all models are attached to Base

    init.configure_user_model(settings)

    # Horus models are optional
    AuthBase = init.configure_horus(settings)
    engine = init.configure_database(settings)

    DBSession.configure(bind=engine)
    if AuthBase:
        AuthBase.metadata.create_all(engine)

    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()