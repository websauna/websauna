"""Support for INI file inclusion mechanism."""
import plaster
import plaster_pastedeploy
from paste.deploy import loadwsgi
from urllib.parse import urlparse
from logging.config import fileConfig
import configparser
import os
import pkg_resources

from pyramid.settings import aslist
from .configincluder import PatchedNicerConfigParser


#: Cache accessed resources
_resource_manager = pkg_resources.ResourceManager()


class NonExistingInclude(Exception):
    pass


class ConfigLoader(loadwsgi.ConfigLoader):
    def __init__(self, filename):
        self.filename = filename = filename.strip()
        defaults = {
            'here': os.path.dirname(os.path.abspath(filename)),
            '__file__': os.path.abspath(filename)
            }
        self.parser = PatchedNicerConfigParser(filename, defaults=defaults)
        self.parser.optionxform = str  # Don't lower-case keys
        with open(filename) as f:
            self.parser.read_file(f)


class Loader(plaster_pastedeploy.Loader):
    def __init__(self, uri):
        uri.scheme = 'file'
        super().__init__(uri)

    def _get_loader(self, defaults=None):
        defaults = self._get_defaults(defaults)
        loader = ConfigLoader(self.uri.path)
        loader.update_defaults(defaults)
        return loader

    def _get_parser(self, defaults=None):
        return self._get_loader(defaults).parser

    def setup_logging(self, defaults=None):
        """
        Set up logging via :func:`logging.config.fileConfig`.

        Defaults are specified for the special ``__file__`` and ``here``
        variables, similar to PasteDeploy config loading. Extra defaults can
        optionally be specified as a dict in ``defaults``.

        :param defaults: The defaults that will be used when passed to
            :func:`logging.config.fileConfig`.
        :return: ``None``.

        """

        if 'loggers' in self.get_sections():
            parser = self._get_parser()
            fileConfig(parser, dict(__file__=self.uri.path, here=os.path.dirname(self.uri.path)), disable_existing_loggers=False)

        else:
            logging.basicConfig()

    def get_wsgi_app(self, name=None, defaults=None):
        return self._get_loader().get_app(name, defaults)

    def get_wsgi_filter(self, name=None, defaults=None):
        return self._get_loader().get_filter(name, defaults)

    def get_wsgi_server(self, name=None, defaults=None):
        return self._get_loader().get_server(name, defaults)

    def __repr__(self):
        return '{}.{}(uri="{}")'.format(self.__class__.__module__, self.__class__.__qualname__, self.uri)

