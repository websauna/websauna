"""Support for INI file inclusion mechanism."""
from urllib.parse import urlparse
from logging.config import fileConfig
import configparser
import os
import pkg_resources

from pyramid.settings import aslist


#: Cache accessed resources
_resource_manager = pkg_resources.ResourceManager()


class NonExistingInclude(Exception):
    pass


class IncludeAwareConfigParser(configparser.SafeConfigParser):
    """Include .ini settings file in others.

    The class name should be ``SorryConfigParserHack``.

    This is a hack to get quick include support for Pyramid INI settings files. This is a variation of Python ``ConfigParser`` which knows about ``[includes]`` section. In this section you can tell the config file to include other config files.

    To add includes add a section in your INI::

        [includes]
        include_ini_files =
            resource://websauna/conf/production.ini
            resource://websauna/conf/base.ini


    Each included file is referred by URL. Currently support protocols are:

    * ``resource:``:  This scheme indicates a Python resource specification. The includes are provided `as Python packages resources <https://pythonhosted.org/setuptools/pkg_resources.html>`_.

    The keys in the current INI file sections are added from includes if the keys do not exist yet. Includes are processed from first to last, first taking precedences.

    The include is not recursive. E.g. the includes of include are not processed at the moment.
    """

    def _read(self, fp, fpname):
        super(IncludeAwareConfigParser, self)._read(fp, fpname)
        self.process_includes(fpname)

    def resolve(self, include_file, fpname):

        parts = urlparse(include_file)

        assert parts.scheme == "resource", "Only resource: supported ATM, got {} in {}".format(include_file, fpname)

        package = parts.netloc
        args = package.split('.') + [parts.path.lstrip('/')]
        path = os.path.join(*args)

        req = pkg_resources.Requirement.parse(package)
        assert _resource_manager.resource_exists(req, path), "Could not find {}".format(include_file)

        config_source = _resource_manager.resource_stream(req, path)
        return config_source

    def read_include(self, include_file, fpname):
        """Augment the current config entries from another INI file."""
        fp = self.resolve(include_file, fpname)
        config = configparser.ConfigParser()

        # For some reason configparser refuses to work with file handles opened by pkg_resource
        text = fp.read().decode("utf-8")
        config.read_string(text, source=include_file)

        for s in config.sections():

            source_section = s
            target_section = s

            if not target_section in self.sections():
                self.add_section(target_section)

            # What we have currently - include must not override existing settings
            current_settings = [key for key, value in self.items(target_section, raw=True)]

            # Go through included settings and add them if the setting is not yet there
            for key, value in config.items(source_section, raw=True):

                if key not in current_settings:
                    self._sections[target_section][key] = value

                    # This causes value interpolation and breaks when it tries to interpolate logging settings because it cannot separate logging formatter string from Python INI internal interpolation
                    # self.set(s, key, value)

    def process_includes(self, fpname):

        if not "includes" in self.sections():
            # no [includes]
            return

        include_ini_files = aslist(self.get("includes", "include_ini_files"))

        for include in include_ini_files:
            self.read_include(include, fpname)

    @classmethod
    def retrofit_settings(cls, global_config, section="app:main"):
        """Update settings dictionary given to WSGI application constructor by Paster to have included settings.

        :param global_config: global_config dict as given by Paster

        :return: New instance of settings
        """

        assert global_config
        assert "__file__" in global_config

        parser = cls()
        parser.read(global_config["__file__"])
        return {k:v for k,v in parser.items(section)}


# Monkey-patched python.paster.setup_logging()
def setup_logging(config_uri, global_conf=None, fileConfig=fileConfig,
                  configparser=configparser):
    """
    Set up logging via the logging module's fileConfig function with the
    filename specified via ``config_uri`` (a string in the form
    ``filename#sectionname``).

    ConfigParser defaults are specified for the special ``__file__``
    and ``here`` variables, similar to PasteDeploy config loading.
    """

    from pyramid.paster import _getpathsec

    path, _ = _getpathsec(config_uri, None)
    parser = IncludeAwareConfigParser()
    parser.read([path])

    if parser.has_section('loggers'):
        config_file = os.path.abspath(path)
        return fileConfig(parser, dict(__file__=config_file, here=os.path.dirname(config_file)), disable_existing_loggers=False)


def monkey_patch_paster_config_parser():
    """Tell Paster to play by my rules.

    Call this before calling ``loadapp()``.

    FASDFWQ#€=IA this shit. Can't wait to BURN paster configs and start something based on YAML. Like with REAL include directives, not this half asset shit.
    """

    from paste.deploy import loadwsgi
    from pyramid import paster

    if hasattr(loadwsgi.NicerConfigParser, "_monkey_patched"):
        return

    def _read(self, fp, fpname):
        super(loadwsgi.NicerConfigParser, self)._read(fp, fpname)
        self.process_includes(fpname)

    loadwsgi.NicerConfigParser._read = _read
    loadwsgi.NicerConfigParser.process_includes = IncludeAwareConfigParser.process_includes
    loadwsgi.NicerConfigParser.read_include = IncludeAwareConfigParser.read_include
    loadwsgi.NicerConfigParser.resolve = IncludeAwareConfigParser.resolve

    paster.setup_logging = setup_logging
    loadwsgi.NicerConfigParser._monkey_patched = True