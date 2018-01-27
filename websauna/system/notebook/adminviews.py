# Pyramid
from pyramid.view import view_config

# Websauna
from websauna.system.admin.modeladmin import ModelAdmin


class Shell:
    """Notebook shell opener.

    Prepolate shell with this object through dbsession query.
    """

    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(context=ModelAdmin.Resource, name="shell", route_name="admin", permission='shell')
    def shell(self):

        from websauna.system.notebook.views import launch_context_sensitive_shell

        obj = self.context.get_object()
        extra_script = "obj = dbsession.query({}).get({})".format(obj.__class__.__name__, obj.id)
        extra_greeting = "* **obj** {}".format(self.context.get_title())
        return launch_context_sensitive_shell(self.request, extra_script, extra_greeting)
