"""ws-create-table script.

Print out sql statements needed to construct all the currently configured models.
"""
# Standard Library
import sys
import typing as t

# SQLAlchemy
from sqlalchemy.sql.ddl import CreateTable

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.scripts import get_config_uri
from websauna.system.devop.scripts import usage_message
from websauna.system.model.meta import Base


def main(argv: t.List[str]=sys.argv):
    """Print out sql statements needed to construct currently configured models.

    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    if len(argv) < 2:
        usage_message(argv)

    config_uri = get_config_uri(argv)
    request = init_websauna(config_uri)
    engine = request.dbsession.get_bind()

    for name, cls in Base._decl_class_registry.items():

        if name == "_sa_module_registry":
            continue

        print(CreateTable(cls.__table__, bind=engine))


if __name__ == "__main__":
    main()
