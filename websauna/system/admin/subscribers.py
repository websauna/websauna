# Pyramid
from pyramid.events import subscriber

# Websauna
from websauna.system.admin import menu
from websauna.system.admin.events import AdminConstruction
from websauna.system.admin.modeladmin import ModelAdminRoot
from websauna.system.core.traversal import Resource


@subscriber(AdminConstruction)
def contribute_model_admin(event):
    """Add model menus to the admin user interface."""

    admin = event.admin
    request = event.admin.request

    model_admin_root = ModelAdminRoot(request)
    Resource.make_lineage(admin, model_admin_root, "models")
    admin.children["models"] = model_admin_root

    # Create a model entries to menu
    data_menu = admin.get_admin_menu().get_entry("admin-menu-data").submenu
    for id, model_admin in model_admin_root.items():
        entry = menu.TraverseEntry("admin-menu-data-{}".format(id), label=model_admin.title, resource=model_admin, name="listing")
        data_menu.add_entry(entry)
