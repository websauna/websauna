# Pyramid
from pyramid.events import subscriber

# Websauna
from websauna.system.admin import menu
from websauna.system.admin.events import AdminConstruction


@subscriber(AdminConstruction)
def contribute_admin(event):
    """Add notebook entry to the admin user interface."""
    admin = event.admin
    entry = menu.RouteEntry(
        "admin-notebook",
        label="Shell",
        icon="fa-terminal",
        route_name="admin_shell",
        condition=lambda entry, request: request.has_permission('shell')
    )
    admin.get_quick_menu().add_entry(entry)
