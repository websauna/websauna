"""ws-dump-db script.

Wrapper for pgsql-dump.bash script. Extract database settings from registry and pass to Bash script.
"""
# Standard Library
import logging
import os
import subprocess
import sys
import typing as t

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.exportenv import create_settings_env
from websauna.system.devop.scripts import get_config_uri
from websauna.system.devop.scripts import usage_message


DUMP_SCRIPT = os.path.join(os.path.dirname(__file__), 'psql-dump.bash')


logger = logging.getLogger(__name__)


def main(argv: t.List[str]=sys.argv):
    """Wrapper for pgsql-dump.bash script.

    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    if len(argv) < 2:
        usage_message(
            argv,
            additional_params='[ARG1, ARG2]',
            additional_line='All arguments are passed to pg_dump command'
        )

    config_uri = get_config_uri(argv)
    request = init_websauna(config_uri)

    # Export all secrets and settings
    bash_env = create_settings_env(request.registry)

    # subprocess.check_output([DUMP_SCRIPT] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    args = argv[2:]
    cmd = [DUMP_SCRIPT] + args

    logger.info("Running %s", " ".join(cmd))

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, env=bash_env, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')


if __name__ == "__main__":
    main()
