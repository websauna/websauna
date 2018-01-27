"""Command line scripts."""
# Standard Library
import os
import sys
import typing as t
from textwrap import dedent

from pkg_resources import load_entry_point

# Websauna
from websauna.system import SanityCheckFailed
from websauna.system.devop.cmdline import prepare_config_uri


FAIL_MSG = """Sanity check failed

Reason:
{exception}
"""

DEPRECATION_MSG = """
DEPRECATION WARNING

This script is deprecated and will be removed in a future release of Websauna.
Instead, please use the following command;
{script} {config_uri}
"""


def feedback(message: str, display_border: bool=True):
    """Display a feedback message on the console then exit.

    :param message: Message to be displayed to the user.
    :raises sys.SystemExit:
    """
    if display_border:
        border = '=' * 100
        message = '{border}\n{message}\n{border}'.format(border=border, message=message)
    message = dedent(message)
    print(message)


def feedback_and_exit(message: str, status_code: t.Optional[int]=None, display_border: bool=True):
    """Display a feedback message on the console then exit.

    :param message: Message to be displayed to the user.
    :param status_code: Status code to be raised after displaying the message.
    :raises sys.SystemExit:
    """
    feedback(message, display_border)
    sys.exit(status_code)


def get_config_uri(argv: t.List[str]) -> str:
    """Return the config_uri from command line argv.

    :param argv: Sequence of command line string arguments.
    :return: config_uri, i.e: ws://websauna/conf/test.ini
    """
    config_uri = argv[1]
    return prepare_config_uri(config_uri)


def usage_message(argv: t.List[str], additional_params: str='', additional_line: t.Optional[str]=None):
    """Display usage message and exit.

    :param argv: Command line arguments.
    :param additional_params: Additional parameters to be displayed. i.e.: [var=value].
    :param additional_line: Additional line to be added to the end of the message. i.e.: [var=value].
    :raises sys.SystemExit:
    """
    cmd = os.path.basename(argv[0])
    msg = 'usage: {cmd} <config_uri> {params}\n(example: "{cmd} ws://conf/production.ini{line}")'.format(
        cmd=cmd,
        params=additional_params,
        line='' if not additional_line else '\n{0}'.format(additional_line)
    )
    feedback_and_exit(msg, status_code=1, display_border=False)


def display_deprecation_warning(script: str, config_uri: str):
    """Display a deprecation message.

    :param script: Name of the original Pyramid script.
    :param config_uri: URI for the configuration file.
    """
    message = DEPRECATION_MSG.format(script=script, config_uri=config_uri)
    feedback(message, True)


def proxy_to_pyramid_script(script: str, argv: t.List[str]):
    """Proxy call to the original Pyramid script.

    :param script: Name of the original Pyramid script.
    :param argv: Command line arguments.
    :raises sys.SystemExit:
    """
    if len(argv) < 2:
        usage_message(argv)

    # Make sure we are prefixing calls with our plaster schema loader.
    config_uri = get_config_uri(argv)
    argv[1] = config_uri
    display_deprecation_warning(script, config_uri)
    try:
        sys.exit(
            load_entry_point('pyramid', 'console_scripts', script)()
        )
    except SanityCheckFailed as exc:
        feedback_and_exit(FAIL_MSG.format(exception=str(exc)), 1)
