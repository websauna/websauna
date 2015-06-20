import sys

from websauna.utils.configincluder import monkey_patch_paster_config_parser

from pyramid.scripts import ptweens

monkey_patch_paster_config_parser()

def main():
    sys.exit(ptweens.main() or 0)