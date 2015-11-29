"""Timed default devop tasks for the system."""
import logging

from websauna.system.task.celery import celery_app as celery

logger = logging.getLogger(__name__)


@celery.task(name="backup")
def backup_task():
    from . import backup
    logger.info("Running daily backup")
    backup.backup_site()
    logger.info("Daily backup done")