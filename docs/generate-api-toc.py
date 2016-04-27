"""Create nice API table of contents."""

import sys

import jinja2
import pkgutil

import websauna.system
import websauna.utils
import websauna.tests

TEMPLATE="""
.. raw:: html

    <style>
        .toctree-wrapper ul,
        .toctree-wrapper li {
            list-style: none !important;
            font-weight: bold;
            font-style: italic;
            margin-left: 0 !important;
        }
    </style>

===
API
===

Core
----

:doc:`websauna.system.Initializer <./websauna.system>`
    Websauna application entry point as an Initializer class, also serving as the platform configuration for customization.


{% for name, intro in modules.core %}

.. toctree::
    :maxdepth: 1

    {{ name }}

.. raw:: html

    <dl>
        <dd>
            {{ intro }}
        </dd>
    </dl>

{% endfor %}


Utilities
---------

{% for name, intro in modules.utils %}

.. toctree::
    :maxdepth: 1

    {{ name }}

.. raw:: html

    <dl>
        <dd>
            {{ intro }}
        </dd>
    </dl>

{% endfor %}


Testing
-------

{% for name, intro in modules.testing %}

.. toctree::
    :maxdepth: 1

    {{ name }}

.. raw:: html

    <dl>
        <dd>
            {{ intro }}
        </dd>
    </dl>

{% endfor %}
"""


template = jinja2.Template(TEMPLATE)

# http://stackoverflow.com/a/15723105/315168
def get_submodules(mod):
    modules = []
    for loader, module_name, is_pkg in  pkgutil.iter_modules(mod.__path__):

        if module_name.startswith("test_"):
            continue

        mod_name = mod.__name__ + "." + module_name
        # print("Found module ", mod_name)
        module = pkgutil.importlib.import_module(mod_name)
        modules.append(module)

    results = []
    for mod in modules:
        try:
            intro = mod.__doc__.split("\n")[0]
        except:
            sys.exit("Module missing a docstring: {}".format(mod))
        results.append((mod.__name__, intro))
    return results

modules = {}

modules["core"] = get_submodules(websauna.system)
modules["utils"] = get_submodules(websauna.utils)
modules["testing"] = get_submodules(websauna.tests)


print(template.render(dict(modules=modules)))