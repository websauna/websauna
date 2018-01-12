"""ws-db-shell script.

Run pgcli shell on the configured database.
"""
# Standard Library
import os
import sys
import typing as t
from shutil import which

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.scripts import feedback
from websauna.system.devop.scripts import feedback_and_exit
from websauna.system.devop.scripts import get_config_uri
from websauna.system.devop.scripts import usage_message


def main(argv: t.List[str]=sys.argv):
    """Run pgcli shell on the database specified on the configuration file.

    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    """
    if len(argv) < 2:
        usage_message(argv, additional_params='[var=value]')

    config_uri = get_config_uri(argv)
    request = init_websauna(config_uri)
    url = request.registry.settings.get('sqlalchemy.url')

    engine = request.dbsession.get_bind()

    if not which('pgcli'):
        message = 'pgcli is not installed\nPlease install Websauna as pip install websauna[utils] to get this dependency'
        feedback_and_exit(message, display_border=False)

    feedback('Connecting to {engine}'.format(engine=engine), display_border=False)
    os.system('pgcli {url}'.format(url=url))
