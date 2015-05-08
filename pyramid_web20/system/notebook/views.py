from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_notebook import startup
from pyramid_notebook.views import launch_notebook
from pyramid_notebook.views import shutdown_notebook as _shutdown_notebook
from pyramid_notebook.views import notebook_proxy as _notebook_proxy
from pyramid_web20.system.admin import Admin

SCRIPT = """
from pyramid_web20.models import DBSession as session
"""

GREETING="""
* **session** - SQLAlchemy database session
"""


def get_dotted_path(klass):
    return klass.__module__ + "." + klass.__name__


def get_import_statement(klass):
    return "from {} import {}".format(klass.__module__, klass.__name__)


@view_config(route_name="notebook_proxy", permission="shell")
def notebook_proxy(request):
    return _notebook_proxy(request, request.user.username)


@view_config(route_name="admin_shell", permission="shell")
def admin_shell(request):

    # Make sure we have a logged in user
    nb = {}

    # Add some extra imports
    startup.make_startup(nb)
    startup.add_script(nb, SCRIPT)
    startup.add_greeting(nb, GREETING)

    # Add every model registered to the site administration to the notebook context as well
    admin = Admin.get_admin(request.registry)
    for name, model_admin in admin.model_admins.items():
        klass = model_admin.get_model()
        startup.add_script(nb, get_import_statement(klass))
        startup.add_greeting(nb, "* **{}** - {}".format(klass.__name__, get_dotted_path(klass)))

    return launch_notebook(request, request.user.username, notebook_context=nb)


@view_config(route_name="shutdown_notebook", permission="shell")
def shutdown_notebook(request):
    _shutdown_notebook(request, request.user.username)
    return HTTPFound(request.route_url("home"))
