import colander
import deform
from pyramid.view import view_config, view_defaults

from .admin import UserAdmin
from .admin import GroupAdmin

from pyramid_layout.panel import panel_config
from pyramid_web20.system import crud
from pyramid_web20.system.crud import listing
from pyramid_web20.system.admin import views as admin_views

from pyramid_web20 import DBSession
from pyramid_web20.system.form.colander import \
    PropertyAwareSQLAlchemySchemaNode
from pyramid_web20.system.form.widget import RelationshipCheckboxWidget
from pyramid_web20.system.user.utils import get_group_class


@panel_config(name='admin_panel', context=UserAdmin, renderer='admin/user_panel.html')
def default_model_admin_panel(context, request):
    """Admin panel for Users."""
    model_admin = context
    admin = model_admin.__parent__
    model = model_admin.get_model()

    title = model_admin.title
    count = DBSession.query(model).count()
    latest_user = DBSession.query(model).order_by(model.activated_at.desc()).first()
    latest_user_url = request.resource_url(admin.get_admin_resource(latest_user))

    return locals()


class UserListing(admin_views.Listing):
    """Listing view for Users."""
    title = "All users"

    table = listing.Table(
        columns = [
            listing.Column("id", "Id",),
            listing.Column("friendly_name", "Friendly name"),
            listing.Column("email", "Email"),
            listing.ControlsColumn()
        ]
    )

    def order_query(self, query):
        return query.order_by(self.get_model().created_at.desc())

    @view_config(context=UserAdmin, route_name="admin", name="listing", renderer="crud/listing.html", permission='view')
    def listing(self):
        return super(UserListing, self).listing()




class GroupWidget(RelationshipCheckboxWidget):

    def make_entry(self, obj):
        return (obj.id, obj.name)


class UserShow(admin_views.Show):
    """Show one user."""

    includes = ["id",
                "created_at",
                "updated_at",
                "username",
                colander.SchemaNode(colander.String(), name='full_name'),
                "email",
                "last_login_at",
                "last_login_ip",
                colander.SchemaNode(colander.String(), name="registration_source"),
                colander.SchemaNode(colander.String(), name="social"),
                #colander.SchemaNode(Groups(), name="groups"),
                "groups",
                ]

    def get_title(self):
        return "{} #{}".format(self.get_object().friendly_name, self.get_object().id)

    def customize_schema(self, schema):
        group_model = get_group_class(self.request.registry)
        schema["groups"].widget = GroupWidget(model=group_model)

    @view_config(context=UserAdmin.Resource, route_name="admin", name="show", renderer="crud/show.html", permission='view')
    def show(self):
        return super(UserShow, self).show()


class Groups(colander.SequenceSchema):
    pass


class UserEdit(admin_views.Edit):
    """Show one user."""

    includes = admin_views.Edit.includes + [
                "username",
                colander.SchemaNode(colander.String(), name='full_name'),
                "email",
                "groups"
                ]

    def get_title(self):
        return "{} #{}".format(self.get_object().friendly_name, self.get_object().id)

    @view_config(context=UserAdmin.Resource, route_name="admin", name="edit", renderer="crud/edit.html", permission='edit')
    def edit(self):
        return super(UserEdit, self).edit()

    def customize_schema(self, schema):
        group_model = get_group_class(self.request.registry)
        schema["groups"].widget = GroupWidget(model=group_model, dictify=schema.dictify)
        schema["groups"].missing = []

class GroupListing(admin_views.Listing):
    """Listing view for Groups."""

    table = listing.Table(
        columns = [
            listing.Column("id", "Id",),
            listing.Column("name", "Name"),
            listing.Column("description", "Description"),
            listing.ControlsColumn()
        ]
    )

    def order_query(self, query):
        return query.order_by(self.get_model().id.desc())

    @view_config(context=GroupAdmin, route_name="admin", name="listing", renderer="crud/listing.html", permission='view')
    def listing(self):
        return super(GroupListing, self).listing()



class GroupShow(admin_views.Show):

    includes = [
        "id",
        "name",
        "description",
        "created_at",
        "updated_at"
    ]

    @view_config(context=GroupAdmin.Resource, route_name="admin", name="show", renderer="crud/show.html", permission='view')
    def show(self):
        return super(GroupShow, self).show()


class GroupAdd(admin_views.Add):

    includes = [
        "name",
        "description"
    ]

    @view_config(context=GroupAdmin, route_name="admin", name="add", renderer="crud/add.html", permission='add')
    def add(self):
        return super(GroupAdd, self).add()


class GroupEdit(admin_views.Edit):

    includes = admin_views.Edit.includes + [
        "name",
        "description"
    ]

    @view_config(context=GroupAdmin.Resource, route_name="admin", name="edit", renderer="crud/edit.html", permission='edit')
    def edit(self):
        return super(GroupEdit, self).edit()

