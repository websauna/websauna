# Standard Library
import os

# Pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from pyramid_notebook import startup
from pyramid_notebook.views import notebook_proxy as _notebook_proxy
from pyramid_notebook.views import shutdown_notebook as _shutdown_notebook
from pyramid_notebook.views import launch_notebook

# Websauna
from websauna.system.model.meta import Base


# Don't do changedir as it doesn't work. TODO: fix bad change_dir in upstream
WEBSAUNA_BOOSTRAP = """
from pkg_resources import load_entry_point
from pyramid_notebook.utils import change_directory

# We need to use this to trigger a proper namespaced package loading
# due to different approaches between pip / easy_install / python setup.py develop
# (it doesn't matter which entry point we load as long as it's from websauna package)
entry_point  = load_entry_point('websauna', 'console_scripts', 'ws-shell')

from websauna.system.devop.cmdline import init_websauna_script_env

# Our development.ini, production.ini, etc.
config_file = '{config_uri}'

with change_directory('{cwd}'):
    script_env = init_websauna_script_env(config_file)
    globals().update(script_env)

"""


#: Include our database session in notebook so it is easy to query stuff right away from the prompt
SCRIPT = """
dbsession = request.dbsession
from websauna.utils.time import now
import sqlalchemy
"""


GREETING = """
* **sqlalchemy** - sqlachemy module
* **dbsession** - SQLAlchemy database session
* **now()** - UTC time as timezone aware datetime object
* **initializer** - websauna.system.Initializer instance
"""


def launch_context_sensitive_shell(request, extra_script="", extra_greeting=""):
    """Launch a IPython Notebook.

    :param extra_script: Extra script executed on the launch of this notebook
    :param extra_greeting: Extra text in the greeting Markdown for this launch
    """
    nb = {}

    # Pass around the Pyramid configuration we used to start this application
    global_config = request.registry.settings["websauna.global_config"]

    # Get the reference to our Pyramid app config file and generate Notebook
    # bootstrap startup.py script for this application
    config_file = global_config["__file__"]
    startup.make_startup(nb, config_file, bootstrap_py=WEBSAUNA_BOOSTRAP, cwd=os.getcwd())
    startup.add_script(nb, SCRIPT)
    startup.add_greeting(nb, GREETING)

    #: Include all our SQLAlchemy models in the notebook variables
    startup.include_sqlalchemy_models(nb, Base)

    startup.add_script(nb, extra_script)
    startup.add_greeting(nb, extra_greeting)

    return launch_notebook(request, request.user.username, notebook_context=nb)


# TODO: Broken at the moment because CSRF conflict
@view_config(route_name="notebook_proxy", permission="shell", require_csrf=False)
def notebook_proxy(request):
    """Proxy IPython Notebook requests to the upstream server.

    A special ``shell`` permission is needed to access this view. See :ref:`websauna.superusers`.
    """
    return _notebook_proxy(request, request.user.username)


@view_config(route_name="admin_shell", permission="shell")
def admin_shell(request):
    """Open admin shell with default parameters for the user.

    A special ``shell`` permission is needed to access this view. See :ref:`websauna.superusers`.
    """
    # Make sure we have a logged in user
    return launch_context_sensitive_shell(request)


@view_config(route_name="shutdown_notebook", permission="shell")
def shutdown_notebook(request):
    """Shutdown the notebook of the current user."""
    _shutdown_notebook(request, request.user.username)
    return HTTPFound(request.route_url("home"))
