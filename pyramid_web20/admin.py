"""Admin mappings."""

from pyramid.security import Allow

from .crud.sqlalchemy import SQLALchemyCRUD


class Admin:
    """Admin interface main object."""

    __acl__ = [
        (Allow, 'group:admin', 'view'),
    ]

    def __init__(self):
        self.mappings = {}

    def register_sqlalchemy_model(self, model):
        self.mappings[model] = SQLALchemyCRUD.create(model)

    @classmethod
    def admin_root_factory(cls, request):
        """Get the admin object for the routes."""
        return cls.get_admin(request)

    @classmethod
    def get_admin(cls, request):
        """Get hold of admin object."""
        return request.registry.settings["pyramid_web20.admin"]
