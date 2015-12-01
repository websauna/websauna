import sys

from pyramid.security import Allow
from websauna.system import crud
from websauna.system.admin import menu
from websauna.system.admin.interfaces import IAdmin
from websauna.system.core.root import Root
from websauna.system.crud import sqlalchemy as sqlalchemy_crud
from websauna.system.crud.sqlalchemy import CRUD as CRUD
from websauna.system.crud.sqlalchemy import Resource as AlchemyResource
from websauna.system.core import traverse




def admin_root_factory(request):
    """Get the admin object for the routes."""
    admin = Admin.get_admin(request.registry)
    return admin



class Admin(traverse.Resource):
    """Admin interface main object.

    Presents /admin part of the URL. Manages model admin registrations and discovery. Provides helper functions to map SQLAlchemy objects to their admin URLs.

    ``Admin`` declares two default menu systems which can be used to register application specific and third party add on entries

    * ``Admin.get_quick_menu()`` returns a vertical menu which is visible in the main site navigation

    * ``Admin.get_admin_menu()`` returns a horizontal menu which is visible after entering the admin UI

    """

    # Root defines where admin interface lies in the URL space
    # __parent__ = Root.get_root()
    __name__ = "admin"

    title = "Admin"

    __acl__ = [
        (Allow, 'group:admin', 'add'),
        (Allow, 'group:admin', 'view'),
        (Allow, 'group:admin', 'edit'),
    ]

    def __init__(self, request):
        super(Admin, self).__init__(request)
        self.model_admins = {}
        self.setup_menu()

    @classmethod
    def get_admin(cls, request):
        """Get hold of admin singleton."""
        return registry.queryUtility(IAdmin)

    def scan(self, config, module):
        """Picks up admin definitions from the module.

        TODO: This is poor-man's Venusian replacement until we get proper implementation.
        """

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
            traverse.Resource.make_lineage(self, model_admin, id, allow_reinit=True)

            self.model_admins[id] = model_admin

            # Create a model listing entry
            data_menu = self.get_admin_menu().get_entry("admin-menu-data").submenu
            entry = menu.TraverseEntry("admin-menu-data-{}".format(id), label=model_admin.title, context=model_admin, name="listing")
            data_menu.add_entry(entry)

    def get_admin_for_model(self, model):
        for model_admin in self.model_admins.values():
            if model_admin.model == model:
                return model_admin

        raise KeyError("No admin defined for model: {}, got {} ".format(model, self.model_admins.values()))

    def get_admin_resource(self, obj):
        """Get a admin traversable item for a SQLAlchemy object.

        To get admin URL of an SQLAlchemy object::

        :param obj: SQLAlchemy model instance
        """
        assert obj is not None, "get_admin_resource() you gave me None, I give you nothing"

        model = obj.__class__
        model_admin = self.get_admin_for_model(model)

        path = model_admin.mapper.get_path_from_object(obj)
        return model_admin[path]

    def get_admin_object_url(self, request, obj, view_name=None):
        """Get URL for viewing the object in admin.

        *obj* must be a model instance which has a registered admin interface.

        :param: URL where to manage this object in admin interface or None if we cannot do mapping for some reason or input is None.
        """
        if not obj:
            return None

        res = self.get_admin_resource(obj)
        if view_name:
            return request.resource_url(res, view_name)
        else:
            return request.resource_url(res)

    def __getitem__(self, name):
        """Traverse to individual model admins by the model name."""
        model_admin = self.model_admins[name]
        return model_admin

    def setup_menu(self):
        """Setup admin main menu."""

        self.admin_menu_entry = menu.NavbarEntry("admin-menu-navbar", label=None, submenu=menu.Menu(), css_class="navbar-admin")
        self.quick_menu_entry = menu.RouteEntry("admin-menu-quick", "Admin", "admin_home", icon="fa-wrench", submenu=menu.Menu())

        home = menu.RouteEntry("admin-quick-menu-home", "Dashboard", "admin_home", icon="fa-wrench")
        self.quick_menu_entry.submenu.add_entry(home)

        home = menu.RouteEntry("admin-menu-home", "Dashboard", "admin_home", icon="fa-wrench")
        self.admin_menu_entry.submenu.add_entry(home)

        data = menu.RouteEntry("admin-menu-data", "Data", "admin_home", submenu=menu.Menu(), icon="fa-list")

        self.admin_menu_entry.submenu.add_entry(data)

    def get_quick_menu_entry(self) -> menu.Entry:
        """Return Admin root menu."""
        return self.quick_menu_entry

    def get_quick_menu(self) -> menu.Menu:
        return self.quick_menu_entry.submenu

    def get_admin_menu_entry(self) -> menu.Entry:
        return self.admin_menu_entry

    def get_admin_menu(self) -> menu.Menu:
        return self.admin_menu_entry.submenu


class ModelAdmin(CRUD):
    """Present one model in admin interface.

    Provide automatized list, show add, edit and delete actions for an SQLAlchemy model which declares admin interface.
    """

    #: URL traversing id
    id = None

    #: Title used in breadcrumbs, other places
    title = None

    #: Our resource factory
    class Resource(AlchemyResource):
        pass

    def get_admin(self):
        """Get Admin resource object."""
        return self.__parent__

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

    def get_title(self):
        if self.title:
            return self.title
        return self.id.capitalize()



