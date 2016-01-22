"""ws-create-table script."""
import getpass

import os
import sys

from sqlalchemy.sql.ddl import CreateTable
from websauna.system.devop.cmdline import init_websauna
from websauna.system.model.meta import Base


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):

    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    request = init_websauna(config_uri)
    engine = request.dbsession.get_bind()

    for name, cls in Base._decl_class_registry.items():

        if name == "_sa_module_registry":
            continue

        print(CreateTable(cls.__table__, bind=engine))


if __name__ == "__main__":
    main()