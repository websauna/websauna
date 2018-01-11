"""Support for INI file inclusion mechanism."""
# Standard Library
import logging
import os
import typing as t
from logging.config import fileConfig

import plaster_pastedeploy
from paste.deploy import loadwsgi

# Websauna
from websauna.utils.config.includer import IncludeAwareConfigParser


class ConfigLoader(loadwsgi.ConfigLoader):
    """Configuration Loader."""

    def __init__(self, filename: str):
        """Initialize the config loader."""
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
        """Initialize the Loader."""
        # Replace our scheme for file, so it could be handled as usual.
        uri.scheme = 'file'
        super().__init__(uri)

    def _get_loader(self, defaults: t.Optional[dict]=None) -> ConfigLoader:
        """Return a ConfigLoader instance.

        :param defaults: Dict with default values.
        :return: ConfigLoader instance.
        """
        defaults = self._get_defaults(defaults)
        loader = ConfigLoader(self.uri.path)
        loader.update_defaults(defaults)
        return loader

    def _get_parser(self, defaults: t.Optional[dict]=None) -> IncludeAwareConfigParser:
        """Return an instance of IncludeAwareConfigParser.

        :param defaults: Dict with default values.
        :return: IncludeAwareConfigParser instance.
        """
        return self._get_loader(defaults).parser

    def setup_logging(self, defaults: t.Optional[dict]=None, disable_existing_loggers=False):
        """Set up logging via :func:`logging.config.fileConfig`.

        Defaults are specified for the special ``__file__`` and ``here``
        variables, similar to PasteDeploy config loading. Extra defaults can
        optionally be specified as a dict in ``defaults``.

        :param defaults: The defaults that will be used when passed to :func:`logging.config.fileConfig`.
        :param disable_existing_loggers: Should existing loggers be disabled.
        """
        defaults = defaults if defaults else {}
        if 'loggers' in self.get_sections():
            uri_path = self.uri.path
            parser = self._get_parser()
            defaults.update(
                {
                    '__file__': uri_path,
                    'here': os.path.dirname(uri_path),
                    'disable_existing_loggers': disable_existing_loggers
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

    def __repr__(self) -> str:
        """Representation of this object.

        :return: String representation of this object.
        """
        klass_module = self.__class__.__module__
        klass_qualname = self.__class__.__qualname__
        return '{0}.{1}(uri="{2}")'.format(klass_module, klass_qualname, self.uri)
