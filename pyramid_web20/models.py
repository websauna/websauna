import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import INET
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


#: Initialze user_data JSONB structure with these fields
DEFAULT_USER_DATA = {
    "full_name": None,
    "user_registration_source": None,
    "social": {
    }
}


class User(UserMixin, Base):

    REGISTRATION_SOURCE_EMAIL = "email"
    REGISTRATION_SOURCE_FACEBOOK = "facebook"
    REGISTRATION_SOURCE_GITHUB = "github"

    #: When this account was created
    created_at = Column(DateTime, default=_now)

    #: When the account data was updated last time
    updated_at = Column(DateTime, onupdate=_now)

    #: When this user accessed the system last time. None if the user has never logged in (only activation email sent). Information stored for the security audits.
    last_login_at = Column(DateTime, nullable=True)

    #: From which IP address did this user log in from. If this IP is null the user has never logged in (only activation email sent). Information stored for the security audits.
    last_login_ip = Column(INET, nullable=True)

    #: When this user changed the password for the last time. The value is null if the user comes from social networks. Information stored for the security audits.
    last_password_change_at = Column(DateTime, nullable=True)

    #: Store all user related settings in this expandable field
    user_data = Column(JSONB, default=DEFAULT_USER_DATA)

    #: Full name of the user (if given)
    full_name = JSONBProperty("user_data", "full_name")

    #: How this user signed up to the site. May include string like "email", "facebook"
    user_registration_source = JSONBProperty("user_data", "user_registration_source")

    def get_friend_name(self):
        """How we present the user's name to the user itself.

        Pick one of 1) full name 2) username 3) email.
        """

        full_name = self.full_name
        if full_name:
            return full_name

        if self.username.startswith("user-"):
            return self.email
        else:
            return self.username


class Group(GroupMixin, Base):
    pass

    group_data = Column(JSONB)


class UserGroup(UserGroupMixin, Base):
    pass


class Activation(ActivationMixin, Base):
    pass
