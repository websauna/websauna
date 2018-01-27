"""Duplicity based backuping."""
# Standard Library
import logging
import os
import stat
import subprocess

# Pyramid
from pyramid.path import AssetResolver
from pyramid.threadlocal import get_current_registry

# Websauna
from websauna.system.devop.exportenv import create_settings_env


__here__ = os.path.dirname(__file__)

logger = logging.getLogger(__name__)


def backup_site():
    """Run the site backup script.

    Runs the configured backup script ``websauna.backup_script``. The backup script can be any UNIX executable. The script gets the environment variables from *websauna* configuration, as exposed by :py:func:`websauna.utils.exportenv.create_settings_env`.

    In the case the backup script fails, an exception is raised and logged through normal application logging means.

    Run backup from the command line::

        echo "from websauna.system.devop import backup ; backup.backup_site()" | pyramid-web20-shell development.ini

    Note that the output is buffered, so there might not be instant feedback.
    """

    registry = get_current_registry()

    backup_script_spec = registry.settings.get("websauna.backup_script", "").strip()
    if not backup_script_spec:
        # Currently we do not have backup script defined, do not run
        return

    resolver = AssetResolver(None)
    backup_script = resolver.resolve(backup_script_spec).abspath()

    assert os.path.exists(backup_script), "Backup script does not exist: {}, spec {}".format(backup_script, backup_script_spec)

    assert stat.S_IXUSR & os.stat(backup_script)[stat.ST_MODE], "Backup script is not executable: {}".format(backup_script)

    backup_timeout = int(registry.settings.get("websauna.backup_timeout"))

    # Export all secrets and settings
    env = create_settings_env(registry)

    try:
        subprocess.check_output([backup_script, ], timeout=backup_timeout, stderr=subprocess.STDOUT, env=env)
    except subprocess.CalledProcessError as e:
        # Capture error to Sentry
        logger.error(e.output)
        raise
