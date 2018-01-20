"""CRUD views for user and group management."""
# Pyramid
import colander
import deform
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.request import Response
from pyramid.view import view_config
from pyramid_layout.panel import panel_config

# SQLAlchemy
from sqlalchemy.orm import Query

# Websauna
from websauna.system.admin import views as admin_views
from websauna.system.admin.utils import get_admin_url_for_sqlalchemy_object
from websauna.system.core import messages
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import listing
from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator
from websauna.system.crud.sqlalchemy import Resource
from websauna.system.crud.sqlalchemy import sqlalchemy_deleter
from websauna.system.crud.views import CSVListing
from websauna.system.crud.views import TraverseLinkButton
from websauna.system.form.fieldmapper import EditMode
from websauna.system.form.fields import JSONValue
from websauna.system.form.fields import defer_widget_values
from websauna.system.form.widgets import JSONWidget
from websauna.system.user import events
from websauna.system.user.admins import GroupAdmin
from websauna.system.user.admins import UserAdmin
from websauna.system.user.interfaces import IPasswordHasher
from websauna.system.user.interfaces import IUser
from websauna.system.user.models import User
from websauna.system.user.schemas import GroupSet
from websauna.system.user.schemas import group_vocabulary
from websauna.system.user.schemas import validate_unique_user_email
from websauna.system.user.utils import get_user_registry
from websauna.utils.time import now


def kill_user_sessions(request: Request, user: IUser, operation: str):
    """Notify session to drop this user.

    :param request: Pyramid request.
    :param user: User.
    :param operation: Operation triggering the killing of user sessions.
    """
    user.last_auth_sensitive_operation_at = now()
    e = events.UserAuthSensitiveOperation(request, user, operation)
    request.registry.notify(e, request)


@panel_config(name='admin_panel', context=UserAdmin, renderer='admin/user_panel.html')
def user_admin_panel(context: UserAdmin, request: Request, **kwargs) -> dict:
    """Admin panel for Users.

    :param context: Model admin.
    :param request: Pyramid request.
    :param kwargs: Additional context to be passed to the panel.
    :return: Context for template rendering.
    """
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
        columns=[
            listing.Column("id", "Id",),
            listing.Column("friendly_name", "Friendly name"),
            listing.Column("email", "Email"),
            listing.ControlsColumn()
        ]
    )

    # Include our CSV export button in the user interface
    resource_buttons = admin_views.Listing.resource_buttons + [
        TraverseLinkButton(id="csv-export", name="CSV Export", view_name="csv-export", permission="view")
    ]

    def order_query(self, query: Query) -> Query:
        """Add ordering to an existing SQLAlchemy query.

        :param query: Base query.
        :return: Query ordered by created_at.
        """
        return query.order_by(self.get_model().created_at.desc())

    @view_config(context=UserAdmin, route_name="admin", name="listing", renderer="crud/listing.html", permission='view')
    def listing(self) -> dict:
        """User listing view.

        :return: Context for template rendering.
        """
        return super(UserListing, self).listing()


def _get_user_navigate_target(view: CSVListing, column: listing.Column, obj: User) -> str:
    """Return the admin url to an User object.

    :param view: Current view.
    :param column: Listing Column
    :param obj: User object.
    :return: Admin url to the User object.
    """
    request = view.request
    admin = request.admin
    return get_admin_url_for_sqlalchemy_object(admin, obj)


@view_overrides(context=UserAdmin, route_name="admin")
class UserCSVListing(CSVListing):
    """CSV export of the site users."""

    title = "users-export"

    table = listing.Table(
        columns=[
            listing.Column("id"),
            listing.Column("uuid"),
            listing.Column("link", getter=_get_user_navigate_target),
            listing.Column("enabled"),
            listing.Column("created_at"),
            listing.Column("last_login_at"),
            listing.Column("username"),
            listing.Column("email"),
            listing.Column("friendly_name"),
        ]
    )

    def order_query(self, query: Query) -> Query:
        """Add ordering to an existing SQLAlchemy query.

        :param query: Base query.
        :return: Query ordered by created_at.
        """
        return query.order_by(self.get_model().created_at.desc())


class UserShow(admin_views.Show):
    """Show one user."""

    resource_buttons = admin_views.Show.resource_buttons + [TraverseLinkButton(id="set-password", name="Set password", view_name="set-password")]

    includes = [
        "id",
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
        colander.SchemaNode(JSONValue(), name="user_data", widget=JSONWidget(), description="user_data JSON properties"),
        colander.SchemaNode(GroupSet(), name="groups", widget=defer_widget_values(deform.widget.CheckboxChoiceWidget, group_vocabulary, css_class="groups"))
    ]

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    def get_title(self) -> str:
        """Title for the User object.

        :return: Title for the User object.
        """
        user = self.get_object()
        return "{friendly_name} #{id}".format(
            friendly_name=user.friendly_name,
            id=self.get_object().id
        )

    @view_config(context=UserAdmin.Resource, route_name="admin", name="show", renderer="crud/show.html", permission='view')
    def show(self):
        """User show view.

        :return: Context for template rendering.
        """
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

    def save_changes(self, form: deform.Form, appstruct: dict, user: User):
        """Save the user edit and reflect if we need to drop user session.

        :param form: Form object.
        :param appstruct: Form data.
        :param user: User object.
        """
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

    def get_title(self) -> str:
        """Title for the User object.

        :return: Title for the User object.
        """
        user = self.get_object()
        return "{friendly_name} #{id}".format(
            friendly_name=user.friendly_name,
            id=self.get_object().id
        )

    @view_config(context=UserAdmin.Resource, route_name="admin", name="edit", renderer="crud/edit.html", permission='edit')
    def edit(self):
        """User edit view.

        :return: Context for template rendering.
        """
        return super(UserEdit, self).edit()


@view_overrides(context=UserAdmin)
class UserAdd(admin_views.Add):
    """CRUD for creating new users."""
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
        """Return the Add form for this view.

        :return: Form object.
        """
        # TODO: Still not sure how handle nested values on the automatically generated add form. But here we need it for groups to appear
        return self.create_form(EditMode.add, buttons=("add", "cancel",))

    def initialize_object(self, form: deform.Form, appstruct: dict, obj: User):
        """Initialize User object.

        :param form: Form object.
        :param appstruct: Form data.
        :param obj: User object.
        """
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
        """Save the form data.

        :param form: Form object.
        :param appstruct: Form data.
        :param user: User object.
        """
        # Set hashed password
        user_registry = get_user_registry(self.request)
        user_registry.set_password(obj, appstruct["password"])

        # Drop session
        kill_user_sessions(self.request, obj, "password_change")

    def do_success(self) -> Response:
        """After password change, redirect user.

        :return: Redirect user.
        """
        messages.add(self.request, kind="success", msg="Password changed.", msg_id="msg-password-changed")
        # Redirect back to view page after edit page has succeeded
        return HTTPFound(self.request.resource_url(self.context, "show"))

    @view_config(context=UserAdmin.Resource, route_name="admin", name="set-password", renderer="crud/edit.html", permission='edit')
    def set_password(self):
        """User set password view.

        :return: Context for template rendering.
        """
        return super(admin_views.Edit, self).edit()


@view_overrides(context=UserAdmin.Resource)
class UserDelete(admin_views.Delete):
    """Delete user view.

    Drop user sessions on invocation.
    """
    def deleter(self, context: Resource, request: Request):
        """Execute user deletion.

        * Delete user from database.
        * Remove all user sessions.

        :param context: Traversable resource.
        :param request: Pyramid request.
        """
        sqlalchemy_deleter(self, context, request)
        kill_user_sessions(request, context.get_object(), "user_deleted")


@view_overrides(context=GroupAdmin)
class GroupListing(admin_views.Listing):
    """Listing view for Groups."""

    table = listing.Table(
        columns=[
            listing.Column("id", "Id",),
            listing.Column("name", "Name"),
            listing.Column("description", "Description"),
            listing.ControlsColumn()
        ]
    )

    def order_query(self, query: Query) -> Query:
        """Add ordering to an existing SQLAlchemy query.

        :param query: Base query.
        :return: Query ordered by id descending.
        """
        return query.order_by(self.get_model().id.desc())


class GroupShow(admin_views.Show):
    """Display one Group."""

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
        """Group show view..

        :return: Context for template rendering.
        """
        return super(GroupShow, self).show()


class GroupAdd(admin_views.Add):
    """Create new Group."""

    includes = [
        "name",
        "description"
    ]

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    @view_config(context=GroupAdmin, route_name="admin", name="add", renderer="crud/add.html", permission='add')
    def add(self):
        """Group add view..

        :return: Context for template rendering.
        """
        return super(GroupAdd, self).add()


class GroupEdit(admin_views.Edit):
    """Edit one group in admin interface."""

    includes = [
        "name",
        "description"
    ]

    form_generator = SQLAlchemyFormGenerator(includes=includes)

    @view_config(context=GroupAdmin.Resource, route_name="admin", name="edit", renderer="crud/edit.html", permission='edit')
    def edit(self):
        """Group edit view..

        :return: Context for template rendering.
        """
        return super(GroupEdit, self).edit()
