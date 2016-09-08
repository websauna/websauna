"""CRUD views for user and group management."""
import colander
import deform
from pyramid_layout.panel import panel_config


from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from websauna.system.admin.utils import get_admin_url_for_sqlalchemy_object
from websauna.system.core import messages
from websauna.system.crud.sqlalchemy import sqlalchemy_deleter
from websauna.system.crud.views import TraverseLinkButton
from websauna.system.form.fieldmapper import EditMode
from websauna.system.form.fields import defer_widget_values
from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator
from websauna.system.user.interfaces import IPasswordHasher
from websauna.system.user.models import User
from websauna.system.user.schemas import group_vocabulary, GroupSet, validate_unique_user_email
from websauna.system.user.utils import get_user_registry
from websauna.utils.time import now
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import listing
from websauna.system.admin import views as admin_views

from .admins import UserAdmin
from .admins import GroupAdmin
from . import events


def kill_user_sessions(request, user, operation):
    # Notify session to drop this user
    user.last_auth_sensitive_operation_at = now()
    e = events.UserAuthSensitiveOperation(request, user, operation)
    request.registry.notify(e)


@panel_config(name='admin_panel', context=UserAdmin, renderer='admin/user_panel.html')
def user_admin_panel(context, request, **kwargs):
    """Admin panel for Users."""

    dbsession = request.dbsession

    model_admin = context
    admin = model_admin.get_admin()
    model = model_admin.get_model()

    title = model_admin.title
    count = dbsession.query(model).count()
    latest_user = dbsession.query(model).order_by(model.id.desc()).first()
    latest_user_url = get_admin_url_for_sqlalchemy_object(admin, latest_user)

    return dict(locals(), **kwargs)


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
                "enabled",
                "created_at",
                "updated_at",
                "username",
                colander.SchemaNode(colander.String(), name='full_name'),
                "email",
                "last_login_at",
                "last_login_ip",
                colander.SchemaNode(colander.String(), name="registration_source", missing=colander.drop),
                colander.SchemaNode(colander.String(), name="social"),
                colander.SchemaNode(GroupSet(), name="groups", widget=defer_widget_values(deform.widget.CheckboxChoiceWidget, group_vocabulary, css_class="groups"))
                ]

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    def get_title(self):
        return "{} #{}".format(self.get_object().friendly_name, self.get_object().id)

    @view_config(context=UserAdmin.Resource, route_name="admin", name="show", renderer="crud/show.html", permission='view')
    def show(self):
        return super(UserShow, self).show()


class UserEdit(admin_views.Edit):
    """Edit one user in admin interface."""

    includes = [
        "enabled",
        colander.SchemaNode(colander.String(), name='username'),  # Make username required field
        colander.SchemaNode(colander.String(), name='full_name', missing=""),
        "email",
        colander.SchemaNode(GroupSet(), name="groups", widget=defer_widget_values(deform.widget.CheckboxChoiceWidget, group_vocabulary, css_class="groups"))
        ]

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    def save_changes(self, form:deform.Form, appstruct:dict, user:User):
        """Save the user edit and reflect if we need to drop user session."""
        enabled_changes = appstruct["enabled"] != user.enabled
        email_changes = appstruct["email"] != user.email
        username_changes = appstruct["username"] != user.username

        super(UserEdit, self).save_changes(form, appstruct, user)

        # Notify authentication system to drop all sessions for this user
        if enabled_changes:
            kill_user_sessions(self.request, user, "enabled_change")
        elif email_changes:
            kill_user_sessions(self.request, user, "email_change")
        elif username_changes:
            kill_user_sessions(self.request, user, "username_change")

    def get_title(self):
        return "{} #{}".format(self.get_object().friendly_name, self.get_object().id)

    @view_config(context=UserAdmin.Resource, route_name="admin", name="edit", renderer="crud/edit.html", permission='edit')
    def edit(self):
        return super(UserEdit, self).edit()


@view_overrides(context=UserAdmin)
class UserAdd(admin_views.Add):
    """CRUD add part for creating new users."""

    #: TODO: Not sure how we should manage with explicit username - it's not used for login so no need to have a point to ask

    includes = [
        # "username", --- usernames are never exposed anymore
        colander.SchemaNode(colander.String(), name="email", validator=validate_unique_user_email),
        "full_name",
        colander.SchemaNode(colander.String(), name='password', widget=deform.widget.CheckedPasswordWidget(css_class="password-widget")),
        colander.SchemaNode(GroupSet(), name="groups", widget=defer_widget_values(deform.widget.CheckboxChoiceWidget, group_vocabulary, css_class="groups"))
    ]

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    def get_form(self):
        # TODO: Still not sure how handle nested values on the automatically generated add form. But here we need it for groups to appear
        return self.create_form(EditMode.add, buttons=("add", "cancel",))

    def initialize_object(self, form, appstruct, obj: User):
        password = appstruct.pop("password")
        form.schema.objectify(appstruct, obj)
        hasher = self.request.registry.getUtility(IPasswordHasher)
        obj.hashed_password = hasher.hash_password(password)

        # Users created through admin are useable right away, so activate the user
        obj.activated_at = now()


class UserSetPassword(admin_views.Edit):
    """Set the user password.

    Use the CRUD edit form with one field to set the user password.
    """

    includes = [
        colander.SchemaNode(colander.String(), name='password', widget=deform.widget.CheckedPasswordWidget(css_class="password-widget")),
    ]

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    def save_changes(self, form: deform.Form, appstruct: dict, obj: User):

        # Set hashed password
        user_registry = get_user_registry(self.request)
        user_registry.set_password(obj, appstruct["password"])

        # Drop session
        kill_user_sessions(self.request, obj, "password_change")

    def do_success(self):
        messages.add(self.request, kind="success", msg="Password changed.", msg_id="msg-password-changed")
        # Redirect back to view page after edit page has succeeded
        return HTTPFound(self.request.resource_url(self.context, "show"))

    @view_config(context=UserAdmin.Resource, route_name="admin", name="set-password", renderer="crud/edit.html", permission='edit')
    def set_password(self):
        return super(admin_views.Edit, self).edit()



@view_overrides(context=UserAdmin.Resource)
class UserDelete(admin_views.Delete):
    """Delete user view.

    Drop user sessions on invocation.
    """
    def deleter(self, context, request):
        sqlalchemy_deleter(self, context, request)
        kill_user_sessions(request, context.get_object(), "user_deleted")


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

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    @view_config(context=GroupAdmin.Resource, route_name="admin", name="show", renderer="crud/show.html", permission='view')
    def show(self):
        return super(GroupShow, self).show()


class GroupAdd(admin_views.Add):

    includes = [
        "name",
        "description"
    ]

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    @view_config(context=GroupAdmin, route_name="admin", name="add", renderer="crud/add.html", permission='add')
    def add(self):
        return super(GroupAdd, self).add()


class GroupEdit(admin_views.Edit):

    includes = [
        "name",
        "description"
    ]

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    @view_config(context=GroupAdmin.Resource, route_name="admin", name="edit", renderer="crud/edit.html", permission='edit')
    def edit(self):
        return super(GroupEdit, self).edit()

