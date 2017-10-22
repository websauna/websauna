import sys

from pyramid.scripts import ptweens

def main():
    sys.exit(ptweens.main() or 0)
