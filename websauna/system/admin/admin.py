"""Default admin root implementation."""

# Pyramid
from pyramid.security import Allow
from pyramid.security import Deny
from pyramid.security import Everyone
from zope.interface import implementer

# Websauna
from websauna.system.admin import menu
from websauna.system.admin.events import AdminConstruction
from websauna.system.admin.interfaces import IAdmin
from websauna.system.core.root import Root
from websauna.system.core.traversal import Resource


@implementer(IAdmin)
class Admin(Resource):
    """Admin interface main object.

    Presents /admin part of the URL. Manages model admin registrations and discovery. Provides helper functions to map SQLAlchemy objects to their admin URLs.

    ``Admin`` declares two default menu systems which can be used to register application specific and third party add on entries

    * ``Admin.get_quick_menu()`` returns a vertical menu which is visible in the main site navigation

    * ``Admin.get_admin_menu()`` returns a horizontal menu which is visible after entering the admin UI

    This class is instiated for each request and does not have global state.
    """

    #: Default permissions of who can add, read and write things in admin
    __acl__ = [
        # Declare admin rights
        (Allow, 'group:admin', 'add'),
        (Allow, 'group:admin', 'view'),
        (Allow, 'group:admin', 'edit'),
        (Allow, 'group:admin', 'delete'),
        (Allow, 'superuser:superuser', 'shell'),

        # Disable access to public users
        (Deny, Everyone, 'view'),  # Declared in websauna.system.core.root.Root
    ]

    def __init__(self, request):
        super(Admin, self).__init__(request)

        # Current add_route() view config sets Admin instance as request.root when traversing inside admin.
        # Assume this admin instance lives directly under the root
        self.__parent__ = Root(request)
        self.__name__ = "admin"

        self.admin_menu_entry = None
        self.quick_menu_entry = None

        # Registered child resources, usually put in AdminConstruct event
        self.children = {}

        self.construct()

    def get_title(self):
        return "Admin"

    def construct(self):
        """Call all admin contributors and let them register parts to this admin."""

        self.construct_default_menu()

        # Call all plugins to register themselves
        self.request.registry.notify(AdminConstruction(self))

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
        return child
