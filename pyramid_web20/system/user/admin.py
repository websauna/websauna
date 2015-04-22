from pyramid.security import Allow

from pyramid_web20.system import admin
from pyramid_web20.system import crud
from pyramid_web20.system.crud import Column
from pyramid_web20.system.crud import ControlsColumn
from pyramid_web20.system.crud import sqlalchemy as sqlalchemy_crud

from pyramid_web20.models import DBSession


class UserAdminPanel(admin.AdminPanel):

    template = "admin/user_panel.html"

    def get_user_count(self):
        model = self.get_model()
        return DBSession.query(model).count()

    def get_latest_user(self):
        model = self.get_model()
        latest = DBSession.query(model).order_by(model.activated_at.desc()).first()
        return latest

    def get_latest_user_url(self, request):
        user = self.get_latest_user()
        admin = self.get_admin()
        traversable = admin.get_admin_resource(user)
        return request.resource_url(traversable)


@admin.ModelAdminCRUD.register(model='pyramid_web20.system.user.models.User')
class UserAdmin(admin.DefaultModelAdminCRUD):

    #: Traverse id
    id = "user"
    title = "Users"
    panel = UserAdminPanel(title="Users")

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



@admin.ModelAdminCRUD.register(model='pyramid_web20.system.user.models.Group')
class GroupAdmin(admin.DefaultModelAdminCRUD):

    #: Traverse id
    id = "group"
    panel = admin.AdminPanel(title="Groups")