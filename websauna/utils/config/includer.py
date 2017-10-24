"""Support for INI file inclusion mechanism."""
# Standard Library
import configparser
import io
import os
import typing as t
from urllib.parse import urlparse

# Pyramid
from pyramid.settings import aslist

import pkg_resources
from paste.deploy import loadwsgi

# Websauna
from websauna.utils.config import exceptions as exc
from websauna.utils.config import _resource_manager


_VALID_SCHEMAS_ = (
    'resource',
)


class IncludeAwareConfigParser(loadwsgi.NicerConfigParser):
    """Include .ini settings file in others.

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

    optionxform = str

    def _read(self, fp: io.TextIOWrapper, fpname: str):
        """Read configuration file and process its includes.

        :param fp: TextIOWrapper
        :param fpname: Main configuration filename.
        """
        super()._read(fp, fpname)
        self.process_includes(fpname)

    def resolve(self, include_file: str, fpname: str) -> t.TextIO:
        """Resolve include_file and return a readable file like object.

        :param include_file: File to be include.
        :param fpname: Main configuration filename.
        :return: Return a readable file-like object for the specified resource.
        """
        parts = urlparse(include_file)
        if parts.scheme not in _VALID_SCHEMAS_:
            raise exc.InvalidResourceScheme(
                "Supported resources: {resources}. Got {include} in {fpname}".format(
                    resources=', '.join(_VALID_SCHEMAS_),
                    include=include_file,
                    fpname=fpname
                )
            )

        package = parts.netloc
        args = package.split('.') + [parts.path.lstrip('/')]
        path = os.path.join(*args)

        req = pkg_resources.Requirement.parse(package)

        if not _resource_manager.resource_exists(req, path):
            raise exc.NonExistingInclude(
                "Could not find {include}".format(include=include_file)
            )

        config_source = _resource_manager.resource_stream(req, path)
        return config_source

    def read_include(self, include_file: str, fpname: str):
        """Augment the current config entries from another INI file.

        :param include_file: File to be include.
        :param fpname: Main configuration filename.
        """
        fp = self.resolve(include_file, fpname)
        config = configparser.ConfigParser()

        # For some reason configparser refuses to work with file handles opened by pkg_resource
        text = fp.read().decode('utf-8')
        config.read_string(text, source=include_file)

        for s in config.sections():
            source_section = s
            target_section = s

            if target_section not in self.sections():
                self.add_section(target_section)

            # What we have currently - include must not override existing settings
            current_settings = [key for key, value in self.items(target_section, raw=True)]

            # Go through included settings and add them if the setting is not yet there
            for key, value in config.items(source_section, raw=True):
                if key not in current_settings:
                    self._sections[target_section][key] = value

    def process_includes(self, fpname: str):
        """Process includes section.

        :param fpname: Main configuration filename.
        """
        if 'includes' in self.sections():
            include_ini_files = aslist(self.get('includes', 'include_ini_files'))
            for include in include_ini_files:
                self.read_include(include, fpname)

    @classmethod
    def retrofit_settings(cls, global_config: dict, section: str='app:main') -> dict:
        """Update settings dictionary given to WSGI application constructor by Paster to have included settings.

        :param global_config: global_config dict as given by Paster
        :param section: Section to be processed.
        :return: New instance of settings
        """
        assert global_config
        assert '__file__' in global_config

        parser = cls()
        parser.read(global_config["__file__"])
        return {k: v for k, v in parser.items(section)}
