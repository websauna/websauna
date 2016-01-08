"""CRUD views for user and group management."""

import colander
import deform

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from websauna.system.admin.utils import get_admin_url_for_sqlalchemy_object
from websauna.system.core import messages
from websauna.system.crud.views import TraverseLinkButton
from websauna.system.user.models import User
from websauna.viewconfig import view_overrides
from .admins import UserAdmin
from .admins import GroupAdmin

from pyramid_layout.panel import panel_config
from websauna.system.crud import listing
from websauna.system.admin import views as admin_views

from websauna.system.form.widget import RelationshipCheckboxWidget
from websauna.system.user.utils import get_group_class



class GroupWidget(RelationshipCheckboxWidget):
    """Specialized widget for selecting user groups."""
    def make_entry(self, obj):
        return (obj.id, obj.name)


@panel_config(name='admin_panel', context=UserAdmin, renderer='admin/user_panel.html')
def user_admin_panel(context, request):
    """Admin panel for Users."""

    dbsession = request.dbsession

    model_admin = context
    admin = model_admin.get_admin()
    model = model_admin.get_model()

    title = model_admin.title
    count = dbsession.query(model).count()
    latest_user = dbsession.query(model).order_by(model.id.desc()).first()
    latest_user_url = get_admin_url_for_sqlalchemy_object(admin, latest_user)

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


class UserShow(admin_views.Show):
    """Show one user."""

    resource_buttons = admin_views.Show.resource_buttons + [TraverseLinkButton(id="set-password", name="Set password", view_name="set-password")]

    includes = ["id",
                "uuid",
                "created_at",
                "updated_at",
                "username",
                colander.SchemaNode(colander.String(), name='full_name'),
                "email",
                "last_login_at",
                "last_login_ip",
                colander.SchemaNode(colander.String(), name="registration_source", missing=colander.drop),
                colander.SchemaNode(colander.String(), name="social"),
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


class UserEdit(admin_views.Edit):
    """Show one user."""

    includes = admin_views.Edit.includes + [
                colander.SchemaNode(colander.String(), name='username'),  # Make username required field
                colander.SchemaNode(colander.String(), name='full_name', missing=""),
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


@view_overrides(context=UserAdmin)
class UserAdd(admin_views.Add):
    """CRUD add part for creating new users."""

    includes = [
        "username",
        "email",
        "full_name",
        colander.SchemaNode(colander.String(), name='password', widget=deform.widget.CheckedPasswordWidget(css_class="password-widget")),
        "groups"
    ]

    def customize_schema(self, schema):
        group_model = get_group_class(self.request.registry)
        schema["groups"].widget = GroupWidget(model=group_model, dictify=schema.dictify)
        schema["groups"].missing = []


class UserSetPassword(admin_views.Edit):
    """Set the user password.

    Use the CRUD edit form with one field to set the user password.
    """

    includes = [
        colander.SchemaNode(colander.String(), name='password', widget=deform.widget.CheckedPasswordWidget(css_class="password-widget")),
    ]

    def save_changes(self, form:deform.Form, appstruct:dict, obj:User):
        super(UserSetPassword, self).save_changes(form, appstruct, obj)
        obj.trigger_auth_sensitive_operation()

    def do_success(self):
        messages.add(self.request, kind="success", msg="Password changed.", msg_id="msg-password-changed")
        # Redirect back to view page after edit page has succeeded
        return HTTPFound(self.request.resource_url(self.context, "show"))

    @view_config(context=UserAdmin.Resource, route_name="admin", name="set-password", renderer="crud/edit.html", permission='edit')
    def set_password(self):
        return super(admin_views.Edit, self).edit()


@view_overrides(context=GroupAdmin)
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

