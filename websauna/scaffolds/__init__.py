"""Scaffold template definitions."""
import binascii
import os

from pyramid.scaffolds import PyramidTemplate


class App(PyramidTemplate):
    _template_dir = 'app'
    summary = 'Websauna app'

    def pre(self, command, output_dir, vars):
        if vars['package'] == 'site':
            raise ValueError('Sorry, you may not name your package "site". '
                             'The package name "site" has a special meaning in '
                             'Python.  Please name it anything except "site".')

        vars['authentication_random'] = binascii.hexlify(os.urandom(20))
        vars['authomatic_random'] = binascii.hexlify(os.urandom(20))
        vars['session_random'] = binascii.hexlify(os.urandom(20))

        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return PyramidTemplate.pre(self, command, output_dir, vars)


class Addon(PyramidTemplate):
    _template_dir = 'addon'
    summary = 'Websauna addon'