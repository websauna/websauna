"""Admin URL endpoints for user and group management."""

from websauna.system.admin.modeladmin import ModelAdmin, model_admin
from websauna.system.crud.urlmapper import Base64UUIDMapper
from websauna.system.user.models import User, Group


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
        """Wrap one SQLAlhcemy user mode to admin resource.

        ``get_object()`` returns :py:class:`websauna.system.user.model.User`.
        """

        def get_title(self):
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
        """Wrap one SQLAlhcemy group model to admin resource.

        ``get_object()`` returns :py:class:`websauna.system.user.model.Group`.
        """

