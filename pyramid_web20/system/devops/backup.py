"""Duplicity based backuping."""
import datetime
from celery.task import periodic_task
import os
import logging
import subprocess

from pyramid.threadlocal import get_current_registry
from pyramid.path import AssetResolver
from pyramid_web20.utils.exportenv import create_settings_env
import stat


__here__ = os.path.dirname(__file__)

logger = logging.getLogger(__name__)


def backup_site():
    """Run the site backup script.

    Runs the configured backup script ``pyramid_web20.backup_script``. The backup script can be any UNIX executable. The script gets the environment variables from *pyramid_web20* configuration, as exposed by :py:func:`pyramid_web20.utils.exportenv.create_settings_env`.

    In the case the backup script fails, an exception is raised and logged through normal application logging means.

    Run backup from the command line::

        echo "from pyramid_web20.system.devops import backup ; backup.backup_site()" | pyramid-web20-shell development.ini

    Note that the output is buffered, so there might not be instant feedback.
    """

    registry = get_current_registry()

    backup_script_spec = registry.settings.get("pyramid_web20.backup_script", "").strip()
    if not backup_script_spec:
        # Currently we do not have backup script defined, do not run
        return

    resolver = AssetResolver(package=None)
    backup_script = resolver.resolve(backup_script_spec).abspath()

    assert os.path.exists(backup_script), "Backup script does not exist: {}".format(backup_script)

    assert stat.S_IXUSR & os.stat(backup_script)[stat.ST_MODE], "Backup script is not executable: {}".format(backup_script)

    backup_timeout = int(registry.settings.get("pyramid_web20.backup_timeout"))

    # Export all secrets and settings
    env = create_settings_env(registry)

    try:
        subprocess.check_output([backup_script,], timeout=backup_timeout, stderr=subprocess.STDOUT, env=env)
    except subprocess.CalledProcessError as e:
        # Capture error to Sentry
        logger.error(e.output)
        raise


