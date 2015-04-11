import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime
from sqlalchemy import Column

from pyramid.i18n import TranslationStringFactory

from horus.models import GroupMixin
from horus.models import UserMixin
from horus.models import UserGroupMixin
from horus.models import ActivationMixin
from horus.models import BaseModel

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from .utils.jsonb import JSONBProperty

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base(cls=BaseModel)

_ = TranslationStringFactory('web20')


def _now():
    """UTC timestamp."""
    return datetime.datetime.utcnow()


class User(UserMixin, Base):

    REGISTRATION_SOURCE_EMAIL = "email"
    REGISTRATION_SOURCE_FACEBOOK = "facebook"
    REGISTRATION_SOURCE_GITHUB = "github"

    #: When this account was created
    created_at = Column(DateTime, default=_now)

    #: When the account data was updated last time
    updated_at = Column(DateTime, onupdate=_now)

    #: Store all user related settings in this expandable field
    user_data = Column(JSONB)

    #: How this user signed up to the site. May include string like "email", "facebook"
    user_registration_source = JSONBProperty("user_data", "user_registration_source")


class Group(GroupMixin, Base):
    pass

    group_data = Column(JSONB)


class UserGroup(UserGroupMixin, Base):
    pass


class Activation(ActivationMixin, Base):
    pass
