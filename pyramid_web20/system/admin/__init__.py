from pyramid.security import Allow


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
    def get_admin(cls, registry):
        """Get hold of admin singleton."""
        return registry.settings["pyramid_web20.admin"]


def admin_root_factory(request):
    """Get the admin object for the routes."""
    admin = Admin.get_admin(request.registry)
    return admin
