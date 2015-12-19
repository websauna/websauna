"""Bootstrap sub for ws-alembic command."""
import sys
from pkg_resources import load_entry_point

from websauna.utils.configincluder import monkey_patch_paster_config_parser
from websauna.utils.configincluder import IncludeAwareConfigParser


# We need to monkey-patch Alembic ConfigParser
from alembic.util import compat
compat.SafeConfigParser = IncludeAwareConfigParser

def main():
    sys.exit(
        load_entry_point('alembic', 'console_scripts', 'alembic')()
    )
