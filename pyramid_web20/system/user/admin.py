from pyramid.security import Allow

from pyramid_web20.system import admin
from pyramid_web20.system import crud
from pyramid_web20.system.crud import Column
from pyramid_web20.system.crud import ControlsColumn
from pyramid_web20.system.crud import sqlalchemy as sqlalchemy_crud

from pyramid_web20.models import DBSession



@admin.ModelAdmin.register(model='pyramid_web20.system.user.models.User')
class UserAdmin(admin.DefaultModelAdmin):

    #: Traverse id
    id = "user"
    title = "Users"
    listing = sqlalchemy_crud.Listing(
        title = "All users",
        columns = [
            Column("id", "Id",),
            Column("friendly_name", "Friendly name"),
            Column("email", "Email"),
            ControlsColumn()
        ]
    )

    show = crud.Show(
        includes=["id", "email", "last_login_ip"]
    )



@admin.ModelAdmin.register(model='pyramid_web20.system.user.models.Group')
class GroupAdmin(admin.DefaultModelAdmin):

    #: Traverse id
    id = "group"
    title = "Groups"

    listing = sqlalchemy_crud.Listing(
        title = "All groups",
        columns = [
            Column("id", "Id",),
            Column("name", "Name"),
            ControlsColumn()
        ]
    )