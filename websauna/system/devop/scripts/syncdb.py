"""ws-sync-db script.

Create initial tables for the database specified on the configuration file.
"""
# Standard Library
import sys
import typing as t

# Pyramid
import transaction

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.scripts import get_config_uri
from websauna.system.devop.scripts import usage_message
from websauna.system.model.meta import Base


def main(argv: t.List[str]=sys.argv):
    """Create initial tables for the database specified on the configuration file.

    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    if len(argv) < 2:
        usage_message(argv)

    config_uri = get_config_uri(argv)
    request = init_websauna(config_uri)

    with transaction.manager:
        engine = request.dbsession.get_bind()
        # Always enable UUID extension for PSQL
        # TODO: Convenience for now, because we assume UUIDs, but make this somehow configurable
        engine.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

        Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
