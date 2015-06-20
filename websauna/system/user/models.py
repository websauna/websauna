"""Default user models.

Avoid importing this module directly. Instead use:

    user_class = request.registry.queryUtility(IUserClass)

"""

from horus import models as horus_models

from . import usermixin
from websauna.system.model import Base

#: TODO: How to handle the fact that Horus requires custom declarative base?
# Base = declarative_base(cls=horus_models.BaseModel)


# XXX: Fix upstream code - Horus uses harcoded table name in declarative attributes
horus_models.UserMixin.__tablename__ = "users"


class User(usermixin.UserMixin, horus_models.UserMixin, horus_models.BaseModel, Base):

    # In PSQL user is a reserved word
    __tablename__ = "users"


class Group(usermixin.GroupMixin, horus_models.GroupMixin, horus_models.BaseModel, Base):
    pass


class UserGroup(horus_models.UserGroupMixin, horus_models.BaseModel, Base):
    pass


class Activation(horus_models.ActivationMixin, horus_models.BaseModel, Base):
    pass

# We don't want these attributes from the default horus's UserMixin
# TODO: Patch upstream for more configurability here
del User.last_login_date
