"""Admin interface. """
from pyramid.view import view_config
from pyramid.security import Allow
from pyramid.renderers import render

from ..models import DBSession


@view_config(route_name='admin', renderer='admin/admin.html', permission='view')
def admin(request):
    admin = Admin.get_admin(request)
    panels = [p.render(request) for p in admin.panels]
    return dict(panels=panels)


@view_config(route_name='admin_model', renderer='admin/admin.html')
def admin_model(self):
    """ """
    return {}


class Admin:
    """Admin interface main object.

    We know what panels are registered on the main admin screen.
    """

    __acl__ = [
        (Allow, 'group:admin', 'view'),
    ]

    def __init__(self):
        self.panels = []

    def register_admin_panel(self, panel):
        self.panels.append(panel)

    @classmethod
    def admin_root_factory(cls, request):
        """Get the admin object for the routes."""
        return cls.get_admin(request)

    @classmethod
    def get_admin(cls, request):
        """Get hold of admin object."""
        return request.registry.settings["pyramid_web20.admin"]


class AdminPanel:
    """ """

    sort_id = None


class SQLAlchemyModelAdminPanel(AdminPanel):

    def __init__(self, model):
        self.model = model

    @property
    def sort_id(self):
        return str(self.model)

    @property
    def title(self):
        return str(self.model.__tablename__)

    def render(self, request):
        count = DBSession.query(self.model).count()
        return render("admin/model_panel.html", dict(self=self, panel=self, count=count), request=request)'

    @classmethod
    def discover(cls, admin, base, registry):
        reg = base._decl_class_registry
        for cls in reg.values():

            if not hasattr(cls, "__tablename__"):
                continue

            if issubclass(cls, base):
                panel = SQLAlchemyModelAdminPanel(cls)
                admin.register_admin_panel(panel)

