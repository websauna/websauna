"""ws-alembic script.

Wrapper for underlying ``alembic`` script, that is able to handle configuration with includes.
"""
# Standard Library
import sys

# SQLAlchemy
from alembic.util import compat

from pkg_resources import load_entry_point

# Websauna
from websauna.utils.config.includer import IncludeAwareConfigParser


# We need to monkey-patch Alembic ConfigParser
compat.SafeConfigParser = IncludeAwareConfigParser


def main():
    sys.exit(
        load_entry_point('alembic', 'console_scripts', 'alembic')()
    )
