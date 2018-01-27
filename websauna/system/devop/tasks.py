"""Timed default devop tasks for the system."""
# Standard Library
import logging

# Websauna
from websauna.system.task.tasks import task


logger = logging.getLogger(__name__)


@task(name="backup")
def backup_task():
    from . import backup
    logger.info("Running daily backup")
    backup.backup_site()
    logger.info("Daily backup done")
