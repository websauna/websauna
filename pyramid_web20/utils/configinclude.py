"""Support for includes hack in [app:main] INIs"""

import configparser
import pkg_resources

from pyramid.settings import aslist


def augment(settings):
    """Scan for includes sections in config and parse them.

    Hardcored crappy solution until I come up with a real extensible config system.

    Paster INI files are f*"#€" horrible. #"#%€(" why they created should awful piece of crap? In 10 years somebody might have come with a better solution, but noo..
    """

    includes = aslist(settings.get("includes", []))
    if includes:
        for inc in includes:
            proto, path = inc.split("#")
            proto, package = proto.split(":")

            assert proto == "egg"

            config_source = pkg_resources.resource_stream(pkg_resources.Requirement.parse(package), path)

            text = config_source.read().decode("utf-8")

            config = configparser.ConfigParser()
            config.read_string(text)

            for key, value in config.items("app:main"):
                if key not in settings:
                    settings[key] = value
