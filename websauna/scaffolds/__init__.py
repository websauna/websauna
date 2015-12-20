"""Scaffold template definitions."""
import binascii
import os

from pyramid.scaffolds import PyramidTemplate
from pyramid.scaffolds.template import bytes_
from pyramid.scaffolds.template import substitute_escaped_double_braces
from pyramid.scaffolds.template import substitute_double_braces
from pyramid.scaffolds.template import _add_except
from pyramid.scaffolds.template import TypeMapper
from pyramid.scaffolds.template import fsenc
from pyramid.scaffolds.template import native_


class JinjaFriendlyTemplate(PyramidTemplate):

    def render_template(self, content, vars, filename=None):
        """ Return a bytestring representing a templated file based on the input (content) and the variable names defined (vars).  ``filename`` is used for exception reporting."""
        content = native_(content, fsenc)
        try:
            # Our hacky attempt to escape {{ and }} in Jinja templates so that this process doesn't mangle them
            text = substitute_escaped_double_braces(substitute_double_braces(content, TypeMapper(vars)))
            text = text.replace("{[", "{{")
            text = text.replace("]}", "}}")
            return bytes_(text, fsenc)
        except Exception as e:
            _add_except(e, ' in file %s' % filename)
            raise


class App(JinjaFriendlyTemplate):
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


