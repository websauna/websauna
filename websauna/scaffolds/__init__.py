"""Provide scaffolds for different Websauna projects."""
import binascii
import shutil

import os
import string

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



def check_valid_package_name(name):
    assert all(c in string.ascii_lowercase + string.ascii_uppercase + string.digits for c in name), "The scaffold assumes the project name must be ASCII letters and numbers only. This is for the sake of clarify when generating the package, not a hard requirement and can be changed later easily edited in the configuration file. websauna. namespace prefix is automatically added to addon packages."


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

        if os.path.exists(os.path.join(self.template_dir(), ".gitignore")):
            # .gitignore needs special handling because leading dot
            shutil.copy(os.path.join(self.template_dir(), ".gitignore"), output_dir)

        separator = "=" * 79
        msg = dedent(
            """
            %(separator)s
            Welcome to Websauna. See README.rst for further information.
            %(separator)s
        """ % {'separator': separator})

        self.out(msg)


class App(JinjaFriendlyTemplate):
    """A scaffold for standalone Websauna app."""

    _template_dir = 'app'
    summary = 'Websauna app'

    def pre(self, command, output_dir, vars):

        check_valid_package_name(vars['project'])

        if vars['package'] == 'site':
            raise ValueError('Sorry, you may not name your package "site". '
                             'The package name "site" has a special meaning in '
                             'Python.  Please name it anything except "site".')

        vars['authentication_random'] = binascii.hexlify(os.urandom(20)).decode("utf-8")
        vars['authomatic_random'] = binascii.hexlify(os.urandom(20)).decode("utf-8")
        vars['session_random'] = binascii.hexlify(os.urandom(20)).decode("utf-8")

        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return PyramidTemplate.pre(self, command, output_dir, vars)


class Addon(JinjaFriendlyTemplate):
    """A scaffold for Websauna addon living in Websauna namespace."""

    _template_dir = 'addon'
    summary = 'Websauna addon'

    def pre(self, command, output_dir, vars):

        check_valid_package_name(vars['project'])

        vars['authentication_random'] = binascii.hexlify(os.urandom(20)).decode("utf-8")
        vars['authomatic_random'] = binascii.hexlify(os.urandom(20)).decode("utf-8")
        vars['session_random'] = binascii.hexlify(os.urandom(20)).decode("utf-8")
        return PyramidTemplate.pre(self, command, output_dir, vars)

    def run(self, command, output_dir, vars):
        # We support websauna namespaced packages only
        output_dir = output_dir.replace("/" + vars["package"], "/websauna." + vars["package"])
        self.pre(command, output_dir, vars)
        self.write_files(command, output_dir, vars)
        self.post(command, output_dir, vars)

