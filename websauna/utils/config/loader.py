"""Support for INI file inclusion mechanism."""
import logging
import os

import plaster_pastedeploy

from paste.deploy import loadwsgi
from logging.config import fileConfig
from websauna.utils.config.includer import IncludeAwareConfigParser


class ConfigLoader(loadwsgi.ConfigLoader):
    """Configuration Loader."""

    def __init__(self, filename):
        self.filename = filename = filename.strip()
        defaults = {
            'here': os.path.dirname(os.path.abspath(filename)),
            '__file__': os.path.abspath(filename)
        }
        self.parser = IncludeAwareConfigParser(filename, defaults=defaults)
        with open(filename) as f:
            self.parser.read_file(f)


class Loader(plaster_pastedeploy.Loader):
    """Loader returning a WSGI application."""

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
        defaults = defaults if defaults else {}
        if 'loggers' in self.get_sections():
            uri_path = self.uri.path
            parser = self._get_parser()
            defaults.update(
                {
                    '__file__': uri_path,
                    'here': os.path.dirname(uri_path),
                    'disable_existing_loggers': False
                }
            )
            fileConfig(
                parser,
                defaults,
            )
        else:
            logging.basicConfig()

    def get_wsgi_app(self, name=None, defaults=None):
        return self._get_loader(defaults).get_app(name, defaults)

    def get_wsgi_filter(self, name=None, defaults=None):
        return self._get_loader(defaults).get_filter(name, defaults)

    def get_wsgi_server(self, name=None, defaults=None):
        return self._get_loader(defaults).get_server(name, defaults)

    def __repr__(self):
        klass_module = self.__class__.__module__
        klass_qualname = self.__class__.__qualname__
        return '{0}.{1}(uri="{2}")'.format(klass_module, klass_qualname, self.uri)

