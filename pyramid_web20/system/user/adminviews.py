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


class Group(colander.MappingSchema):
    id = colander.SchemaNode(colander.Int())
    name = colander.SchemaNode(
        colander.String(),
    )

class Groups(colander.SequenceSchema):
    groups = Group(missing=[])


class GroupWidget(deform.widget.TextInputWidget):
    readonly_template = 'readonly/groups'


class UserShow(admin_views.Show):
    """Show one user."""

    includes = ["id",
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

    def get_form(self):
        obj = self.get_object()
        includes = self.includes
        schema = PropertyAwareSQLAlchemySchemaNode(obj.__class__, includes=includes)
        form = deform.Form(schema)
        schema["groups"].widget = GroupWidget()
        return form

    @view_config(context=UserAdmin.Resource, route_name="admin", name="show", renderer="crud/show.html", permission='view')
    def show(self):
        return super(UserShow, self).show()



class GroupListing(admin_views.Listing):
    """Listing view for Groups."""

    title = "All groups"

    table = listing.Table(
        columns = [
            listing.Column("id", "Id",),
            listing.Column("name", "Name"),
            listing.ControlsColumn()
        ]
    )

    def order_query(self, query):
        return query.order_by(self.get_model().id.desc())

    @view_config(context=GroupAdmin, route_name="admin", name="listing", renderer="crud/listing.html", permission='view')
    def listing(self):
        return super(GroupListing, self).listing()
