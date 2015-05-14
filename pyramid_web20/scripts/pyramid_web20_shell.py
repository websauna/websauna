import os
import sys
from pyramid_web20 import get_init
from pyramid_web20.utils.configincluder import \
    monkey_patch_paster_config_parser
import transaction
from collections import OrderedDict

from IPython import embed

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars
from pyramid_web20.models import DBSession
from pyramid_web20.models import Base
from pyramid.path import DottedNameResolver
from pyramid.paster import bootstrap

from paste.deploy import loadapp

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

    settings = get_appsettings(config_uri, options=options)
    env = bootstrap(config_uri)

    imported_objects = OrderedDict()
    imported_objects.update(env)
    del imported_objects["closer"]
    imported_objects["session"] = DBSession
    imported_objects["transaction"] = transaction

    for name, cls in Base._decl_class_registry.items():
        imported_objects[name] = cls

    print("")
    print("Following classes and objects are available:")
    for var, val in imported_objects.items():
        print("{:30}: {}".format(var, str(val).replace("\n", " ").replace("\r", " ")))
    print("")

    embed(user_ns=imported_objects)

if __name__ == "__main__":
    main()