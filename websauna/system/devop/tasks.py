"""Timed default devop tasks for the system."""
import logging

from pyramid_celery import celery_app as app

logger = logging.getLogger(__name__)


@app.task(name="backup")
def backup_task():
    from . import backup
    logger.info("Running daily backup")
    backup.backup_site()
    logger.info("Daily backup done")