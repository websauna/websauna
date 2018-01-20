"""Default user model implementations.

Define how User, Group, UserGroup and Activation models are in relationship together.

These models are picked up in :py:meth:`websauna.system.Initializer.configure_user_models`.
"""
# Pyramid
from zope.interface import implementer

# SQLAlchemy
import sqlalchemy as sa
from sqlalchemy.ext.declarative.base import _declarative_constructor

# Websauna
from websauna.system.user import usermixin
from websauna.system.user.interfaces import IGroup
from websauna.system.user.interfaces import IUser
from websauna.system.user.usermixin import ActivationMixin
from websauna.system.user.usermixin import UserGroupMixin


@implementer(IUser)
class User(usermixin.UserMixin):
    """The default user implementation for Websauna.

    This is a concrete implementation of SQLAlchemy model.
    """

    # In PSQL "user", the automatically generated table name, is a reserved word
    __tablename__ = "users"

    __init__ = _declarative_constructor

    #: Current user activation instance for reset password for sign up email verification
    activation_id = sa.Column(sa.Integer, sa.ForeignKey("user_activation.id"))

    #: SQLAlchemy relationship for above
    activation = sa.orm.relationship('Activation', backref='user')


@implementer(IGroup)
class Group(usermixin.GroupMixin):
    """The default group implementation for Websauna."""

    __tablename__ = "group"

    __init__ = _declarative_constructor

    users = sa.orm.relationship(
        'User',
        secondary="usergroup",
        passive_deletes=True,
        passive_updates=True,
        backref="groups",
    )

    def __str__(self):
        """Representation of a Group object."""
        return "Group #{id}: {name}".format(id=self.id, name=self.name)


class UserGroup(UserGroupMixin):
    """Map one user to one group."""

    __tablename__ = "usergroup"

    # Default constructor
    __init__ = _declarative_constructor

    user_id = sa.Column(sa.ForeignKey("users.id"))
    group_id = sa.Column(sa.ForeignKey("group.id"))


class Activation(ActivationMixin):
    """The default implementation of user email activation token."""

    __tablename__ = "user_activation"

    # Default constructor
    __init__ = _declarative_constructor
