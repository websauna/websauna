"""ws-dump-db command entry point.

Wrapper for pgsql-dump.bash script. Extract database settings from registry and pass to Bash script.
"""

import subprocess

import os
import sys

from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.exportenv import create_settings_env


DUMP_SCRIPT = os.path.join(os.path.dirname(__file__), "psql-dump.bash")


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [ARG1, ARG2]\n'
          '(example: "%s development.ini") \n'
          'All arguments are passed to pg_dump command' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):

    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]

    request = init_websauna(config_uri)

    # Export all secrets and settings
    bash_env = create_settings_env(request.registry)

    # subprocess.check_output([DUMP_SCRIPT] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    args = argv[2:]
    cmd = [DUMP_SCRIPT] + args
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, env=bash_env, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')


if __name__ == "__main__":
    main()
