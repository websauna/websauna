"""Timed default devop tasks for the system."""
import datetime
from celery.task import periodic_task


@periodic_task(run_every=datetime.timedelta(days=1))
def backup_task():
    from . import backup
    backup.backup_site()