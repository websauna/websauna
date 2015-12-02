from websauna.system.admin.modeladmin import ModelAdmin, model_admin
from websauna.system.user.usermixin import UserMixin, GroupMixin


@model_admin(traverse_id="user", model=UserMixin)
class UserAdmin(ModelAdmin):

    #: Traverse title
    title = "Users"

    singular_name = "user"
    plural_name = "users"

    class Resource(ModelAdmin.Resource):

        def get_title(self):
            return self.get_object().friendly_name


@model_admin(traverse_id="group", model=GroupMixin)
class GroupAdmin(ModelAdmin):

    #: Traverse title
    title = "Groups"

    singular_name = "group"
    plural_name = "groups"

    class Resource(ModelAdmin.Resource):
        pass

