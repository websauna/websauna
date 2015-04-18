from pyramid.security import Allow

from pyramid_web20.system import admin
from pyramid_web20.system import crud
from pyramid_web20.system.crud import Column

from pyramid_web20.models import DBSession

class UserCRUD(crud.CRUD):

    listing = crud.Listing(
        columns = (
            Column("id", "Id",),
            Column("get_friendly_name", "Friendly name"),
            Column("email", "Email"),
        )
    )


class UserAdminPanel(admin.AdminPanel):

    template = "admin/user_panel.html"

    def get_user_count(self):
        model_admin = self.__parent__
        model = model_admin.model
        return DBSession.query(model).count()

    def get_latest_user(self):
        model_admin = self.__parent__
        model = model_admin.model
        latest = DBSession.query(model).order_by(model.activated_at.desc()).first()
        return latest



@admin.ModelAdmin.register(model='pyramid_web20.system.user.models.User')
class UserAdmin(admin.ModelAdmin):

    #: Traverse id
    id = "user"
    panel = UserAdminPanel(title="Users")
    crud = UserCRUD


@admin.ModelAdmin.register(model='pyramid_web20.system.user.models.Group')
class GroupAdmin(admin.ModelAdmin):

    #: Traverse id
    id = "user"
    panel = admin.AdminPanel(title="Users")
    crud = UserCRUD