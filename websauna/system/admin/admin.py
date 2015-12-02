"""Default admin root implementation."""
import sys

from pyramid.security import Allow
from websauna.system.admin import menu
from websauna.system.admin.events import AdminConstruction
from websauna.system.admin.interfaces import IAdmin
from websauna.system.core import traverse
from websauna.system.core.root import Root
from websauna.system.core.traverse import Resource
from zope.interface import implementer


@implementer(IAdmin)
class Admin(traverse.Resource):
    """Admin interface main object.

    Presents /admin part of the URL. Manages model admin registrations and discovery. Provides helper functions to map SQLAlchemy objects to their admin URLs.

    ``Admin`` declares two default menu systems which can be used to register application specific and third party add on entries

    * ``Admin.get_quick_menu()`` returns a vertical menu which is visible in the main site navigation

    * ``Admin.get_admin_menu()`` returns a horizontal menu which is visible after entering the admin UI

    This class is instiated for each request and does not have global state.
    """

    title = "Admin"

    #: Default permissions of who can add, read and write things in admin
    __acl__ = [
        (Allow, 'group:admin', 'add'),
        (Allow, 'group:admin', 'view'),
        (Allow, 'group:admin', 'edit'),
    ]

    def __init__(self, request):
        super(Admin, self).__init__(request)

        # if not hasattr(request, "root"):
        #    import pdb ; pdb.set_trace()

        # assert hasattr(request, "root"), "request {} missing root".format(request)

        # TODO: Inspect the case why we don't see root on request
        # Assume this admin instance lives directly under the root
        self.__parent__ = request.root if hasattr(request, "root") else Root(request)
        self.__name__ = "admin"

        self.admin_menu_entry = None
        self.quick_menu_entry = None

        # Registered child resources, usually put in AdminConstruct event
        self.children = {}

        self.construct()

    def construct(self):
        """Call all admin contributors and let them register parts to this admin."""

        self.construct_default_menu()

        # Call all plugins to register themselves
        self.request.registry.notify(AdminConstruction(self))

    def get_admin_object_url(self, obj, view_name=None):
        """Get URL for viewing the object in admin.

        *obj* must be a model instance which has a registered admin interface.

        :param: URL where to manage this object in admin interface or None if we cannot do mapping for some reason or input is None.
        """

        request = self.request

        if not obj:
            return None

        res = self.get_admin_resource(obj)
        if view_name:
            return request.resource_url(res, view_name)
        else:
            return request.resource_url(res)

    def construct_default_menu(self):
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

    def __getitem__(self, name):
        """Traverse to individual model admins by the model name."""
        child = self.children[name]
        Resource.make_lineage(self, child, name)
        return child





