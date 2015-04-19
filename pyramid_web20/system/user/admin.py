from pyramid.security import Allow

from pyramid_web20.system import admin
from pyramid_web20.system import crud
from pyramid_web20.system.crud import Column
from pyramid_web20.system.crud import ControlsColumn
from pyramid_web20.system.crud import sqlalchemy as sqlalchemy_crud

from pyramid_web20.models import DBSession


class UserCRUD(admin.ModelCRUD):

    listing = sqlalchemy_crud.Listing(
        title="Users",
        base_template="admin/base.html",
        columns = [
            Column("id", "Id",),
            Column("friendly_name", "Friendly name"),
            Column("email", "Email"),
            ControlsColumn()
        ]
    )


class UserAdminPanel(admin.AdminPanel):

    template = "admin/user_panel.html"

    def get_user_count(self):
        model = self.get_model()
        return DBSession.query(model).count()

    def get_latest_user(self):
        model = self.get_model()
        latest = DBSession.query(model).order_by(model.activated_at.desc()).first()
        return latest



@admin.ModelAdmin.register(model='pyramid_web20.system.user.models.User')
class UserAdmin(admin.ModelAdmin):

    #: Traverse id
    id = "user"
    panel = UserAdminPanel(title="Users")
    crud = UserCRUD()


@admin.ModelAdmin.register(model='pyramid_web20.system.user.models.Group')
class GroupAdmin(admin.ModelAdmin):

    #: Traverse id
    id = "group"
    panel = admin.AdminPanel(title="Groups")
    crud = None