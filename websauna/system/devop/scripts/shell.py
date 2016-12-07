"""IPython shell prompt command: ws-shell"""

import os
import sys
from collections import OrderedDict

import datetime
import transaction

try:
    from IPython import embed
except ImportError as e:
    raise ImportError("You need to install IPython to use this shell") from e

from websauna.system.core.redis import get_redis
from websauna.system.devop.cmdline import init_websauna
from websauna.system.model.meta import Base
from websauna.utils.time import now


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
    imported_objects["redis"] = get_redis(request)
    imported_objects["now"] = now
    imported_objects["datetime"] = datetime

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