"""IPython shell prompt command: ws-shell"""

import os
import sys

from websauna.system.devop.cmdline import init_websauna
from websauna.utils.configincluder import \
    monkey_patch_paster_config_parser
import transaction
from collections import OrderedDict

from IPython import embed

from pyramid.paster import (
    setup_logging,
    )

from websauna.system.model.meta import Base


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):

    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]

    request = init_websauna(config_uri)

    imported_objects = OrderedDict()

    imported_objects["request"] = request
    imported_objects["dbsession"] = request.dbsession
    imported_objects["transaction"] = transaction

    for name, cls in Base._decl_class_registry.items():

        if name == "_sa_module_registry":
            continue

        imported_objects[name] = cls

    print("")
    print("Following classes and objects are available:")
    for var, val in imported_objects.items():
        print("{:30}: {}".format(var, str(val).replace("\n", " ").replace("\r", " ")))
    print("")

    embed(user_ns=imported_objects)

if __name__ == "__main__":
    main()