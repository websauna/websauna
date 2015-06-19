from pyramid.security import Allow

from pyramid_web20.system import admin
from pyramid_web20.system import crud
from pyramid_web20.system.crud import sqlalchemy as sqlalchemy_crud

from pyramid_web20.system.model import DBSession




@admin.ModelAdmin.register(model='pyramid_web20.system.user.models.User')
class UserAdmin(admin.ModelAdmin):

    #: Traverse id
    id = "user"

    #: Traverse title
    title = "Users"

    singular_name = "user"
    plural_name = "users"

    class Resource(admin.ModelAdmin.Resource):
        pass


@admin.ModelAdmin.register(model='pyramid_web20.system.user.models.Group')
class GroupAdmin(admin.ModelAdmin):

    #: Traverse id
    id = "group"

    #: Traverse title
    title = "Groups"

    singular_name = "group"
    plural_name = "groups"

    class Resource(admin.ModelAdmin.Resource):
        pass

