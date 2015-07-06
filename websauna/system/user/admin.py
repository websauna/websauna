from websauna.system import admin


@admin.ModelAdmin.register(model='websauna.system.user.models.User')
class UserAdmin(admin.ModelAdmin):

    #: Traverse id
    id = "user"

    #: Traverse title
    title = "Users"

    singular_name = "user"
    plural_name = "users"

    class Resource(admin.ModelAdmin.Resource):

        def get_title(self):
            return self.get_object().friendly_name


@admin.ModelAdmin.register(model='websauna.system.user.models.Group')
class GroupAdmin(admin.ModelAdmin):

    #: Traverse id
    id = "group"

    #: Traverse title
    title = "Groups"

    singular_name = "group"
    plural_name = "groups"

    class Resource(admin.ModelAdmin.Resource):
        pass

