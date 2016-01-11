from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_notebook import startup
from pyramid_notebook.views import launch_notebook
from pyramid_notebook.views import shutdown_notebook as _shutdown_notebook
from pyramid_notebook.views import notebook_proxy as _notebook_proxy
from websauna.system.model.meta import Base


#: Include our database session in notebook so it is easy to query stuff right away from the prompt
SCRIPT = """
dbsession = request.dbsession
"""


GREETING="""
* **dbsession** - SQLAlchemy database session
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
    startup.make_startup(nb, config_file)
    startup.add_script(nb, SCRIPT)
    startup.add_greeting(nb, GREETING)

    #: Include all our SQLAlchemy models in the notebook variables
    startup.include_sqlalchemy_models(nb, Base)

    startup.add_script(nb, extra_script)
    startup.add_greeting(nb, extra_greeting)

    return launch_notebook(request, request.user.username, notebook_context=nb)


@view_config(route_name="notebook_proxy", permission="shell")
def notebook_proxy(request):
    """Proxy IPython Notebook requests to the upstream server."""
    return _notebook_proxy(request, request.user.username)


@view_config(route_name="admin_shell", permission="shell")
def admin_shell(request):
    """Open admin shell with default parameters for the user."""
    # Make sure we have a logged in user
    return launch_context_sensitive_shell(request)


@view_config(route_name="shutdown_notebook", permission="shell")
def shutdown_notebook(request):
    """Shutdown the notebook of the current user."""
    _shutdown_notebook(request, request.user.username)
    return HTTPFound(request.route_url("home"))
