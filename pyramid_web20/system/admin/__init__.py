import sys
from pyramid.renderers import render

from pyramid.security import Allow

class Admin:
    """Admin interface main object.

    We know what panels are registered on the main admin screen.
    """

    __acl__ = [
        (Allow, 'group:admin', 'view'),
    ]

    def __init__(self):
        self.model_admins = {}

    def register_admin_panel(self, id, panel):
        self.panel_container[id] = panel

    @classmethod
    def get_admin(cls, registry):
        """Get hold of admin singleton."""
        return registry.settings["pyramid_web20.admin"]

    def get_panels(self):
        for model_admin in self.model_admins.values():
            if model_admin.panel:
                yield model_admin.panel

    def scan(self, config, module):
        """Picks up admin definitions from the module."""

        __admin__ = getattr(module, "__admin__", None)

        if not __admin__:
            raise RuntimeError("Admin tried to scan module {}, but it doesn't have __admin__ attribute. The module probably doesn't define any admin objects.".format(module))

        for model_dotted, admin_cls in __admin__.items():

            # Instiate model admin
            try:
                model = config.maybe_dotted(model_dotted)
            except ImportError as e:
                raise ImportError("Tried to initialize model admin for {}, but could not import it".format(model_dotted)) from e

            try:
                model_admin = admin_cls(model)
            except Exception as e:
                raise RuntimeError("Could not instiate model admin {} for model {}".format(admin_cls, model)) from e

            id = getattr(model_admin, "id", None)
            if not id:
                raise RuntimeError("Model admin does not define id {}".format(model_admin))

            # Keep ACL chain intact
            model_admin.__parent__ = self
            model_admin.__name__ = id

            self.model_admins[id] = model_admin

    def __getitem__(self, name):

        # Traverse to models
        model_admin = self.model_admins[name]

        return model_admin



class AdminPanelContainer:

    def __init__(self):
        self.panels = {}

    def __getitem__(self, item):
        return self.panels[item]


class ModelAdmin:
    """Present one model in admin interface."""

    #: URL traversing id
    id = None

    #: Admin panel instance used on the admin homepage
    panel = None

    #: CRUD instance used to render model listing, view, add, edit, delete, etc.
    crud = None

    def __init__(self, model):
        self.model = model
        self.init_lineage()

    def init_lineage(self):
        """Make sure that all context objects have parent pointers set."""

        if hasattr(self.panel, "__parent__"):
            raise RuntimeError("Tried to double initialize lineage for model admin {} panel {}".format(self, self.panel))

        self.panel.__parent__ = self
        self.panel.__name__ = "panel"

    def get_model(self):
        return

    @classmethod
    def register(cls, model):
        """Mark the class to become a model admin on Admin.scan()."""

        def inner(wrapped_cls):

            assert cls.__module__, "Class without module attached cannot possibly work"

            # XXX: Now store registered model admins in a module attribute, which will be later picked up scan(). Think some smarter way to do this, like using events and pyramid config registry.
            module = sys.modules[wrapped_cls.__module__]
            __admin__ = getattr(module, "__admin__", {})
            __admin__[model] = wrapped_cls
            module.__admin__ = __admin__

            return wrapped_cls

        return inner

    def __getitem__(self, name):
        if name == "panel":
            return self.panel
        return None

class AdminPanel:

    #: Template hint which template to use for this panel
    template = "admin/model_panel.html"

    def __init__(self, title):
        self.title = title


def admin_root_factory(request):
    """Get the admin object for the routes."""
    admin = Admin.get_admin(request.registry)
    return admin



