"""Generate template reference."""

# Pyramid
import jinja2

# Websauna
import websauna.system
import websauna.system.admin
import websauna.system.crud
import websauna.system.user
import websauna.tests
import websauna.utils
from websauna.system.devop.cmdline import init_websauna


TEMPLATE = """
.. _template-filters:

======================================
Template context variables and filters
======================================

.. raw:: html

    <!-- Make TOC more readable -->
    <style>

        #contents ul > li {
            font-weight: bold;
            margin-top: 20px;
        }

        #contents ul > li > ul {
            font-weight: normal;
            margin-top: 0;

            display: flex;
            flex-wrap: wrap;
            /* TODO: Width here does not seem to take effect, forcing it below */
            flex: 1 0 200px;
            font-size: 90%;
        }

        #contents ul > li > ul > li {

            font-weight: normal;
            margin-top: 0;


            list-style: none;
            margin-left: 0;
            margin-right: 20px;
            box-sizing: border-box;
            width: 250px;
        }

    </style>


.. contents:: :local:

Introduction
============

:doc:`See templating documentation <../narrative/frontend/templates>`.

Variables
=========

{% for name, func, doc, heading in modules.vars %}

.. _var-{{ name }}:

{{ name }}
{{ heading }}

{{ doc }}

{% if func %}
See :py:func:`{{ func }}` for more information.
{% endif %}

{% endfor %}


Filters
=======

{% for name, func, doc, heading in modules.filters %}

.. _filter-{{ name }}:

{{ name }}
{{ heading }}

{{ doc }}

{% if func %}
See :py:func:`{{ func }}` for more information.
{% endif %}

{% endfor %}


.. _notes-on-subscriptions:

"""

template = jinja2.Template(TEMPLATE)
env = jinja2.Environment()


def fullname(o):
    return o.__module__ + "." + o.__name__


def strip_indent(doc):
    lines = doc.split("\n")

    def strip_prefix(line):
        if line.startswith("    "):
            return line[4:]
        return line

    return "\n".join([strip_prefix(l) for l in lines])


def find_filters(request):
    from pyramid_jinja2 import IJinja2Environment
    env = request.registry.queryUtility(IJinja2Environment, name=".html")
    filters = []
    for name, func in env.filters.items():
        heading = "-" * len(name)
        doc = strip_indent(func.__doc__)

        qual = fullname(func)
        if qual.startswith("builtins"):
            qual = qual[len("builtins"):]

        # No API docs for Jinja builtins
        if qual.startswith("jinja2."):
            qual = None

        filters.append((name, qual, doc, heading))

    filters = sorted(filters, key=lambda x: x[0])
    return filters


def find_vars():
    vars = websauna.system.core.vars
    result = []
    for name, func in vars._template_variables.items():
        qual = fullname(func)
        doc = strip_indent(func.__doc__)
        heading = "-" * len(name)
        result.append((name, qual, doc, heading))
    result = sorted(result, key=lambda x: x[0])
    return result


request = init_websauna("../websauna/conf/development.ini")

modules = {}
modules["filters"] = find_filters(request)
modules["vars"] = find_vars()

print(template.render(dict(modules=modules)))
