"""Create nice API table of contents."""

import websauna.system
import websauna.utils
import jinja2
import types

TEMPLATE="""


"""


template = jinja2.Template(TEMPLATE)

# http://stackoverflow.com/a/15723105/315168
def get_submodules(mod):
    modules = []
    for key, obj in mod.__dict__.items():
        if type(obj) is types.ModuleType:
            modules += "key"

    modules = modules.sorted()

packages = []

packages += get_submodules(websauna.system)

