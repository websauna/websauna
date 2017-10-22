"""Config file includer aware wrapper for proutes."""
import sys
from pkg_resources import load_entry_point


def main():
    sys.exit(
        load_entry_point('pyramid', 'console_scripts', 'proutes')()
    )

