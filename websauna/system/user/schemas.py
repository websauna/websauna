import deform
import deform.widget as w
import colander as c
from colander.compat import is_nonstr_iter

from hem.schemas import CSRFSchema
from horus.schemas import unique_email
from websauna.system.form.fields import TuplifiedModel, TuplifiedModelSequenceSchema
from websauna.system.form.sqlalchemy import convert_query_to_tuples, ModelSet, UUIDModelSet
from websauna.system.user.models import Group
from websauna.system.user.utils import get_group_class, get_user_class

#: Todo change to setting, convert to deferred widget
from websauna.utils.slug import uuid_to_slug, slug_to_uuid
from websauna.compat.typing import List

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


def validate_unique_user_email(node, value, **kwargs):
    """Make sure we cannot enter the same username twice."""

    request = node.bindings["request"]
    dbsession = request.dbsession
    User = get_user_class(request.registry)
    if dbsession.query(User).filter_by(email=value).first():
        raise c.Invalid(node, "Email address already taken")


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
        validator=c.All(c.Email(), unique_email),
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
