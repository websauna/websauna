"""Admin URL endpoints for user and group management."""
# Websauna
from websauna.system.admin.modeladmin import ModelAdmin
from websauna.system.admin.modeladmin import model_admin
from websauna.system.crud.urlmapper import Base64UUIDMapper
from websauna.system.user.models import Group
from websauna.system.user.models import User


@model_admin(traverse_id="user")
class UserAdmin(ModelAdmin):
    """Models/user admin root resource."""
    #: Traverse title
    title = "Users"
    singular_name = "user"
    plural_name = "users"
    model = User

    mapper = Base64UUIDMapper()

    class Resource(ModelAdmin.Resource):
        """Wrap one SQLAlchemy user mode to admin resource.

        ``get_object()`` returns :py:class:`websauna.system.user.model.User`.
        """

        def get_title(self) -> str:
            """Return the title to be used on the admin.

            :return: Object friendly_name.
            """
            return self.get_object().friendly_name


@model_admin(traverse_id="group")
class GroupAdmin(ModelAdmin):
    """Models/groups admin root resource."""

    #: Traverse title
    title = "Groups"
    singular_name = "group"
    plural_name = "groups"
    model = Group

    mapper = Base64UUIDMapper()

    class Resource(ModelAdmin.Resource):
        """Wrap one SQLAlchemy group model to admin resource.

        ``get_object()`` returns :py:class:`websauna.system.user.model.Group`.
        """
