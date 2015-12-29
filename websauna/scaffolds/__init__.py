"""Scaffold template definitions."""
import binascii
import os

from textwrap import dedent
from pyramid.scaffolds import PyramidTemplate
from pyramid.scaffolds.template import bytes_
from pyramid.scaffolds.template import substitute_escaped_double_braces
from pyramid.scaffolds.template import substitute_double_braces
from pyramid.scaffolds.template import _add_except
from pyramid.scaffolds.template import TypeMapper
from pyramid.scaffolds.template import fsenc
from pyramid.scaffolds.template import native_
from pyramid.scaffolds.template import Template # API


class JinjaFriendlyTemplate(PyramidTemplate):
    """A template which can handle {{ and }} in Jinja files without confusing them with template variables themselves."""

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

    def post(self, command, output_dir, vars): # pragma: no cover
        """ Overrides :meth:`pyramid.scaffolds.template.Template.post`, to
        print "Welcome to Pyramid.  Sorry for the convenience." after a
        successful scaffolding rendering."""

        separator = "=" * 79
        msg = dedent(
            """
            %(separator)s
            Welcome to Websauna.  See README.txt for further information.
            %(separator)s
        """ % {'separator': separator})

        self.out(msg)
        return Template.post(self, command, output_dir, vars)


class App(JinjaFriendlyTemplate):
    """A scaffold for standalone Websauna app."""

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
    """A scaffold for Websauna addon living in Websauna namespace."""

    _template_dir = 'addon'
    summary = 'Websauna addon'

    def pre(self, command, output_dir, vars):

        vars['authentication_random'] = binascii.hexlify(os.urandom(20))
        vars['authomatic_random'] = binascii.hexlify(os.urandom(20))
        vars['session_random'] = binascii.hexlify(os.urandom(20))
        return PyramidTemplate.pre(self, command, output_dir, vars)

    def run(self, command, output_dir, vars):
        # We support websauna namespaced packages only
        output_dir = output_dir.replace("/" + vars["package"], "/websauna." + vars["package"])
        self.pre(command, output_dir, vars)
        self.write_files(command, output_dir, vars)
        self.post(command, output_dir, vars)

