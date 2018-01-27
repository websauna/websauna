"""Generate template reference."""

# Standard Library
import os

# Pyramid
import jinja2

# Websauna
import websauna.system
import websauna.system.admin
import websauna.system.crud
import websauna.system.user
import websauna.tests
import websauna.utils


TEMPLATE = """

.. _templates:

=========
Templates
=========


.. raw:: html

    <!-- Make TOC more readable -->
    <style>

        #contents ul > li {te
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

Default site
============

{% for name, intro, ref, heading in modules.core %}

.. _template-{{ name }}:

{{ name }}
{{ heading }}

{{ intro }}

.. literalinclude:: {{ ref }}
    :language: html+jinja
    :linenos:
    :name: {{ name }}

{% endfor %}

Admin
=====

{% for name, intro, ref, heading in modules.admin %}

.. _template-{{ name }}:

{{ name }}
{{ heading }}

{{ intro }}

.. literalinclude:: {{ ref }}
    :language: html+jinja
    :linenos:
    :name: {{ name }}

{% endfor %}


CRUD
====

{% for name, intro, ref, heading in modules.crud %}

.. _template-{{ name }}:

{{ name }}
{{ heading }}

{{ intro }}

.. literalinclude:: {{ ref }}
    :language: html+jinja
    :linenos:
    :name: {{ name }}

{% endfor %}

User
====

{% for name, intro, ref, heading in modules.user %}

.. _template-{{ name }}:

{{ name }}
{{ heading }}

{{ intro }}

.. literalinclude:: {{ ref }}
    :language: html+jinja
    :linenos:
    :name: {{ name }}

{% endfor %}
"""


template = jinja2.Template(TEMPLATE)
env = jinja2.Environment()


def find_package_templates(pkg):
    path = pkg.__file__
    templates = os.path.join(os.path.dirname(path), "templates")

    ref_path = os.path.abspath(os.path.join(os.getcwd(), "source", "reference"))

    for root, dirs, files in os.walk(templates, topdown=False):
        for name in files:
            full = os.path.join(root, name)
            rel_path = os.path.relpath(full, templates)
            if name.endswith(".html") or name.endswith(".txt") or name.endswith(".xml"):

                template_source = open(full, "rt").read()
                lexed = env.lex(template_source)
                lexed = list(lexed)

                if lexed[0][1] == "comment_begin":
                    description = lexed[1][2].strip()
                else:
                    description = "--- description missing ---"

                literal_include_path = os.path.relpath(full, ref_path)

                heading = "-" * len(rel_path)

                yield rel_path, description, literal_include_path, heading


modules = {
    'core': list(find_package_templates(websauna.system.core)),
    'admin': list(find_package_templates(websauna.system.admin)),
    'crud': list(find_package_templates(websauna.system.crud)),
    'user': list(find_package_templates(websauna.system.user))
}


print(template.render(dict(modules=modules)))
