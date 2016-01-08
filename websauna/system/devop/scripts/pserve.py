"""Config file includer aware wrapper for pserve."""
import sys
from pkg_resources import load_entry_point

from websauna.utils.configincluder import monkey_patch_paster_config_parser
from websauna.utils.configincluder import IncludeAwareConfigParser

monkey_patch_paster_config_parser()

def main():
    sys.exit(
        load_entry_point('pyramid', 'console_scripts', 'pserve')()
    )
