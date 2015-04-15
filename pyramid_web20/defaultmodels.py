"""Default user models.

Avoid importing this module directly. Instead use:

    user_class = request.registry.queryUtility(IUserClass)

"""
from sqlalchemy.ext.declarative import declarative_base

from horus import models as horus_models

from pyramid_web20 import models

#: TODO: How to handle the fact that Horus requires custom declarative base?
Base = declarative_base(cls=horus_models.BaseModel)


# XXX: Fix upstream code - Horus uses harcoded table name in declarative attributes
horus_models.UserMixin.__tablename__ = "users"


class User(models.UserMixin, horus_models.UserMixin, Base):

    # In PSQL user is a reserved word
    __tablename__ = "users"


class Group(models.GroupMixin, horus_models.GroupMixin, Base):
    pass


class UserGroup(horus_models.UserGroupMixin, Base):
    pass


class Activation(horus_models.ActivationMixin, Base):
    pass

# We don't want these attributes from the default horus's UserMixin
# TODO: Patch upstream for more configurability here
del User.last_login_date
