"""ws-shell script.

IPython shell prompt to Websauna.
"""
# Standard Library
import datetime
import sys
import typing as t
from collections import OrderedDict

# Pyramid
import transaction

# Websauna
from websauna.system.core.redis import get_redis
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.scripts import feedback
from websauna.system.devop.scripts import get_config_uri
from websauna.system.devop.scripts import usage_message
from websauna.system.model.meta import Base
from websauna.utils.time import now


try:
    from IPython import embed
except ImportError as e:
    raise ImportError("You need to install IPython to use this shell") from e


def main(argv: t.List[str]=sys.argv):
    """Execute the IPython shell prompt with Websauna configuration already initialised.

    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    if len(argv) < 2:
        usage_message(argv, additional_params='[var=value]')

    config_uri = get_config_uri(argv)

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

    feedback('', False)
    feedback('Following classes and objects are available:', False)
    for var, val in imported_objects.items():
        line = "{key:30}: {value}".format(
            key=var,
            value=str(val).replace('\n', ' ').replace('\r', ' ')
        )
        feedback(line)
    feedback('', False)

    embed(user_ns=imported_objects)


if __name__ == "__main__":
    main()
