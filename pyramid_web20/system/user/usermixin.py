from sqlalchemy import inspection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy import DateTime
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import MutableDict

import colander

from pyramid_web20.models import now
from pyramid_web20.models import utc
from pyramid_web20.models import DBSession
from pyramid_web20.utils.jsonb import JSONBProperty


#: Initialze user_data JSONB structure with these fields
DEFAULT_USER_DATA = {
    "full_name": None,
    "user_registration_source": None,

    # Is it the first time this user is logging to our system? If it is then take the user to fill in the profile page.
    "first_login": True,

    "social": {
    }
}


# TODO: "user" is reserved name on PSQL. File an issue against Horus.
# UserMixin.__tablename__ = "users"


class UserMixin:
    """A user who signs up with email or with email from social media.

    TODO: Make user user.id is not exposed anywhere e.g. in email activation links.
    """
    #: A test user
    USER_MEDIA_DUMMY = "dummy"

    #: Self sign up
    USER_MEDIA_EMAIL = "email"

    #: User signed up with Facebook
    USER_MEDIA_FACEBOOK = "facebook"

    #: User signed up with Github
    USER_MEDIA_GITHUB = "github"

    #: Admin group name
    GROUP_ADMIN = "admin"

    #: Though not displayed on the site, the concept of "username" is still preversed. If the site needs to have username (think Instragram, Twitter) the user is free to choose this username after the sign up. Username is null until the initial user activation is completed after db.flush() in create_activation().
    username = Column(String(32), nullable=True, unique=True)

    #: Store the salted password. This is nullable because users using social media logins may never set the password.
    _password = Column('password', String(256), nullable=True)

    #: The salt used for the password. Null if no password set.
    salt = Column(String(256), nullable=True)

    #: When this account was created
    created_at = Column(DateTime(timezone=utc), default=now)

    #: When the account data was updated last time
    updated_at = Column(DateTime(timezone=utc), onupdate=now)

    #: When this user was activated: email confirmed or first social login
    activated_at = Column(DateTime(timezone=utc), nullable=True)

    #: Is this user account enabled. The support can disable the user account in the case of suspected malicious activity.
    enabled = Column(Boolean, default=True)

    #: When this user accessed the system last time. None if the user has never logged in (only activation email sent). Information stored for the security audits.
    last_login_at = Column(DateTime(timezone=utc), nullable=True)

    #: From which IP address did this user log in from. If this IP is null the user has never logged in (only activation email sent). Information stored for the security audits. It is also useful for identifying the source country of users e.g. for localized versions.
    last_login_ip = Column(INET, nullable=True,
              info={'colanderalchemy': {
                        'typ': colander.String(),
                    }},
            )

    #: When this user changed the password for the last time. The value is null if the user comes from social networks. Information stored for the security audits.
    last_password_change_at = Column(DateTime, nullable=True)

    #: Store all user related settings in this expandable field
    user_data = Column(MutableDict.as_mutable(JSONB), default=DEFAULT_USER_DATA,
                    info={'colanderalchemy': {
                        'typ': colander.String(),
                    }},
            )

    #: Full name of the user (if given)
    full_name = JSONBProperty("user_data", "/full_name")

    #: How this user signed up to the site. May include string like "email", "facebook"
    registration_source = JSONBProperty("user_data", "/registration_source")

    #: Social media data of the user as a dict keyed by user media
    social = JSONBProperty("user_data", "/social")

    #: Is this the first login the user manages to do to our system. Use this information to redirect to special help landing page.
    first_login = JSONBProperty("user_data", "/first_login")

    @property
    def friendly_name(self):
        """How we present the user's name to the user itself.

        Pick one of 1) full name 2) username if set 3) email.
        """
        full_name = self.full_name
        if full_name:
            return full_name

        if self.username.startswith("user-"):
            return self.email
        else:
            return self.username

    def generate_username(self):
        """The default username we give for the user."""
        assert self.id
        return "user-{}".format(self.id)

    def can_login(self):
        """Is this user allowed to login."""
        return self.enabled and self.is_activated

    def is_admin(self):
        """Does this user the see the main admin interface link.

        TODO: This is very suboptimal, wasted database cycles, etc.
        """

        for g in self.groups:
            if g.name == self.GROUP_ADMIN:
                print("User {} is admin".format(self))
                return True

        return False


class GroupMixin:

    group_data = Column(JSONB,
                    info={'colanderalchemy': {
                        'typ': colander.String(),
                    }},
            )


def init_empty_site(user):
    """When the first user signs up build the admin groups and make the user member of it."""

    # Try to reflect related group class based on User model
    i = inspection.inspect(user.__class__)
    Group = i.relationships["groups"].mapper.entity

    # Do we already have any groups... if we do we probably don'¨t want to init again
    if DBSession.query(Group).count() > 0:
        return

    g = Group(name=user.GROUP_ADMIN)
    DBSession.add(g)
    DBSession.flush()

    g.users.append(user)


def check_empty_site_init(user):
    """Call after user creation to see if this user is the first user and should get initial admin rights."""

    assert user.id, "Please flush your db"

    if DBSession.query(user.__class__).count() != 1:
        return

    init_empty_site(user)
