from websauna.system.admin.modeladmin import ModelAdmin, model_admin
from websauna.system.user.models import User, Group


@model_admin(traverse_id="user")
class UserAdmin(ModelAdmin):

    #: Traverse title
    title = "Users"

    singular_name = "user"
    plural_name = "users"
    model = User

    class Resource(ModelAdmin.Resource):

        def get_title(self):
            return self.get_object().friendly_name


@model_admin(traverse_id="group")
class GroupAdmin(ModelAdmin):

    #: Traverse title
    title = "Groups"
    singular_name = "group"
    plural_name = "groups"
    model = Group

    class Resource(ModelAdmin.Resource):
        pass

