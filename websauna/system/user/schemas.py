import deform
import deform.widget as w
import colander as c

from websauna.system.form.schema import CSRFSchema
from websauna.system.form.sqlalchemy import convert_query_to_tuples, UUIDModelSet
from websauna.system.user.utils import get_user_registry
from websauna.system.user.utils import get_group_class, get_user_class
from websauna.utils.slug import uuid_to_slug


#: Todo change to setting, convert to deferred widget
PASSWORD_MIN_LENGTH = 6


def defer_group_class(node, kw):
    """Colander helper deferred to assign the current group model."""

    request = kw.get("request")
    assert request, "To use this widget you must pass request to Colander schema.bind()"

    return get_group_class(request.registry)


def group_vocabulary(node, kw):
    """Convert all groups on the site to (uuid, name) tuples for checkbox and select widgets."""

    Group = defer_group_class(node, kw)
    request = kw["request"]

    def first_column_getter(group: Group):
        return uuid_to_slug(group.uuid)

    return convert_query_to_tuples(request.dbsession.query(Group).all(), first_column=first_column_getter, second_column="name")


def optional_group_vocabulary(node, kw):
    """Convert all groups on the site to (uuid, name) tuples for checkbox and select widgets. Include a choice for no choice."""
    options = group_vocabulary(node, kw)
    return [("", "[ not selected ]")] + options


def validate_unique_user_email(node, value, **kwargs):
    """Make sure we cannot enter the same username twice."""

    request = node.bindings["request"]
    dbsession = request.dbsession
    User = get_user_class(request.registry)
    value = value.strip()
    if dbsession.query(User).filter_by(email=value).one_or_none():
        raise c.Invalid(node, "Email address already taken")


def email_exists(node, val):
    '''Colander validator that ensures a User exists with the email.'''
    request = node.bindings['request']
    User = request.registry.getUtility(IUserClass)
    exists = request.dbsession.query(User).filter(User.email.ilike(val)).one_or_none()
    if not exists:
        raise c.Invalid(node, "Email does not: {}".format(val))


class GroupSet(UUIDModelSet):
    """A set of Group objects referred by their uuid."""

    label_column = "name"

    def get_model(self, node):
        request = node.bindings["request"]
        return get_group_class(request.registry)


class RegisterSchema(CSRFSchema):
    """Username-less registration form schema."""

    email = c.SchemaNode(
        c.String(),
        title='Email',
        validator=c.All(c.Email(), validate_unique_user_email),
        widget=w.TextInputWidget(size=40, maxlength=260, type='email'))

    password = c.SchemaNode(
        c.String(),
        validator=c.Length(min=PASSWORD_MIN_LENGTH),
        widget=deform.widget.CheckedPasswordWidget(),
    )


class LoginSchema(CSRFSchema):
    """Login form schema.

    The user can log in both with email and his/her username, though we recommend using emails as users tend to forget their usernames.
    """

    username = c.SchemaNode(c.String(), title='Email', validator=c.All(c.Email()), widget=w.TextInputWidget(size=40, maxlength=260, type='email'))

    password = c.SchemaNode(c.String(), widget=deform.widget.PasswordWidget())


class ResetPasswordSchema(CSRFSchema):
    user = c.SchemaNode(
        c.String(),
        missing=c.null,
        widget=deform.widget.TextInputWidget(template='readonly/textinput'))

    password = c.SchemaNode(
        c.String(),
        validator=c.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget()
    )


def validate_user_exists_with_email(node, val):
    '''Colander validator that ensures a User exists with the email.'''
    request = node.bindings['request']

    user_registry = get_user_registry(request)
    user = user_registry.get_by_email(val)

    if not user:
        raise c.Invalid(node, "Cannot reset password for such email: {}".format(val))


class ForgotPasswordSchema(CSRFSchema):
    """Used on forgot password view."""
    email = c.SchemaNode(
        c.Str(),
        title='Email',
        validator=c.All(c.Email(), validate_user_exists_with_email),
        widget=w.TextInputWidget(size=40, maxlength=260, type='email', template="textinput_placeholder"),
        description="The email address under which you have your account. Example: joe@example.com")
