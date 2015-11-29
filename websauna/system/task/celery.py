"""Wrap pyramid_celery loader, so that it works with our INI includer hack."""
try:
    import coverage
    coverage.process_startup()
except ImportError:
    # http://nedbatchelder.com/code/coverage/subprocess.html
    pass


from websauna.utils.configincluder import IncludeAwareConfigParser
from websauna.utils.configincluder import monkey_patch_paster_config_parser

monkey_patch_paster_config_parser()

from pyramid_celery.loaders import INILoader
INILoader.ConfigParser = IncludeAwareConfigParser

from pyramid_celery import *
from .transactionawaretask import TransactionAwareTask

# Set up celery task class which is transaction aware
celery_app.transaction_aware_task = TransactionAwareTask


