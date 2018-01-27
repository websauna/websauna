"""Create nice API table of contents."""

# Standard Library
import pkgutil
import sys

# Pyramid
import jinja2

# Websauna
import websauna.system
import websauna.tests
import websauna.utils


TEMPLATE = """
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

.. toctree::
    :maxdepth: 4

    modules
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
    for loader, module_name, is_pkg in pkgutil.iter_modules(mod.__path__):

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
        except Exception as exc:
            sys.exit("Module missing a docstring: {mod}".format(mod=mod))
        results.append((mod.__name__, intro))
    return results


modules = {
    'core': get_submodules(websauna.system),
    'utils': get_submodules(websauna.utils),
    'testing': get_submodules(websauna.tests)
}


print(template.render(dict(modules=modules)))
