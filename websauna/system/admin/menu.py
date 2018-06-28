"""Simple mechanism to register admin menu entries."""
# Standard Library
import typing as t
from collections import OrderedDict

# Pyramid
from pyramid.renderers import render
from pyramid.request import Request

# Websauna
from websauna.system.core.traversal import Resource


class Menu:
    """Menu is a collection of items in a Bootstrap pull-down menu.

    It allow mechanism for third party packages to register their own entries.
    """

    template = "admin/menu/menu.html"

    def __init__(self):
        self.entries = OrderedDict()

    # TODO: How to define entry type here to be Entry (circular)
    def add_entry(self, entry):
        self.entries[entry.id] = entry

    def has_items(self, request: Request) -> bool:
        """Has this menu any entries to draw."""
        return any(entry.is_enabled(request) for entry in self.entries.values())

    def get_entries(self) -> t.List:
        """Get Entry objects to be rendered in this menu.

        Sort return by natural name order.
        """
        return sorted(self.entries.values(), key=lambda e: e.label)

    def get_entry(self, id):
        """Get any of registered menu entries by its id."""
        return self.entries[id]


class Entry:
    """Option is one choice in a menu.

    It can be a simple link, submenu or a custom rendered template.

    Adding conditional entry with a permission check::

        admin = Admin.get_admin(self.config.registry)
        entry = menu.RouteEntry("admin-notebook", label="Shell", icon="fa-terminal", route_name="admin_shell", condition=lambda request:request.has_permission('shell'))
        admin.get_root_menu().add_entry(entry)
    """

    template = "admin/menu/entry.html"

    caret = "fa fa-caret-down"

    def __init__(self, id: str, label: str, icon: str=None, caret: str=None, css_class: str=None, template: str=None, submenu: Menu=None, condition: t.Callable=None, link: t.Callable=None, extra: dict=None):
        """
        :param id: Machine id and CSS id for this menu entry
        :param label: Human-readable label of the menu item
        :param css_class: CSS class for the main entry HTML element
        :param icon: CSS class for FontAwesome <i> icon. Example: ``fa-wrench``.
        :param caret: CSS class for submenu caret. Example: ```fa fa-caret-right``. Default: ``fa fa-caret-down``
        :param template: Jinja 2 template definition used to render this entry. Defaults to ``admin/menu_options.html``
        :param submenu: If this entry is a submenu, then this points to the menu object.
        :param condition: callable(entry, request) which returns True or False should the menu entry be visible
        :param link: callable(entry, request) which returns string to a where this menu entry should go
        :param extra: Dictionary of extra parameters which can be accessed later on in templates and functions
        """
        assert id
        self.id = id
        self.label = label
        self.icon = icon
        self.submenu = submenu
        self.css_class = css_class
        self.condition = condition
        self.link = link

        if caret:
            self.caret = caret

        if template:
            self.template = template

        self.extra = extra or {}

    def is_enabled(self, request) -> bool:
        """Return True if this entry is visible."""

        # Is this a submenu without entries
        if self.submenu:
            if not self.submenu.has_items(request):
                return False

        # The condition for this entry valuates to False
        if self.condition is not None:
            return self.condition(self, request)

        return True

    def get_link(self, request: Request) -> str:
        """Get the link target where this menu entry jumps to."""

        if self.link:
            return self.link(self, request)

        raise NotImplementedError()

    def render(self, request: Request):
        """Render this item to HTML.

        :return: Rendered HTML as a string
        """
        context = dict(entry=self)
        return render(self.template, context, request=request)


class RouteEntry(Entry):
    """Menu entry which has a Pyramid route as a link. """

    def __init__(self, id: str, label: str, route_name: str, **kwargs):
        """
        :param route_name: Link target name for ``request.route_url()``
        """
        assert route_name
        assert type(route_name) == str
        super(RouteEntry, self).__init__(id, label, **kwargs)
        self.route_name = route_name

    def get_link(self, request):
        return request.route_url(self.route_name)


class TraverseEntry(Entry):
    """Menu entry which has a Pyramid traversing context as a link.

    Please note that this works only for fixed resources which are generated on the application startup.

    Example::

        admin = Admin.get_admin(self.config.registry)
        entry = menu.TraverseEntry(id="admin-menu-phone-order", label="Create phone order", context=admin, name="phone-order", icon="fa-phone")
        admin.get_admin_menu().add_entry(entry)
    """

    def __init__(self, id: str, label: str, resource: Resource, name: str, **kwargs):
        """
        :param context: Any Pyramid resource object
        :param name: Traversable view name
        """
        assert name
        assert type(name) == str
        super(TraverseEntry, self).__init__(id, label, **kwargs)
        self.resource = resource
        self.name = name

    def get_link(self, request):
        return request.resource_url(self.resource, self.name)


class NavbarEntry(Entry):
    """Root entry for rendering horizontal navigation list menu."""

    template = "admin/menu/navbar.html"
