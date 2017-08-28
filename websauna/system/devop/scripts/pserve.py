"""Config file includer aware wrapper for pserve."""
import sys
from pkg_resources import load_entry_point

try:
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    pass


def main():
    sys.exit(
        load_entry_point('pyramid', 'console_scripts', 'pserve')()
    )
