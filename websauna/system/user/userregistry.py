"""Default user object generator."""
# Standard Library
import typing as t
from datetime import timedelta

# Pyramid
from zope.interface import implementer

# SQLAlchemy
from sqlalchemy import func

# Websauna
from websauna.system.user import events
from websauna.system.user.interfaces import IPasswordHasher
from websauna.system.user.interfaces import IUser
from websauna.system.user.interfaces import IUserRegistry
from websauna.system.user.usermixin import GroupMixin
from websauna.system.user.usermixin import UserMixin
from websauna.system.user.utils import get_activation_model
from websauna.system.user.utils import get_user_class
from websauna.utils.time import now


@implementer(IUserRegistry)
class DefaultEmailBasedUserRegistry:
    """Default user backend which uses SQLAlchemy to store User models.

    Provides default user actions
    """

    def __init__(self, request):
        self.dbsession = request.dbsession
        self.registry = request.registry

    @property
    def User(self):
        """Currently configured User SQLAlchemy model."""
        return get_user_class(self.registry)

    @property
    def Activation(self):
        """Currently configured User SQLAlchemy model."""
        return get_activation_model(self.registry)

    def set_password(self, user, password):
        """Hash a password for persistent storage.

        Uses password hasher registered in :py:meth:`websauna.system.Initializer.configure_password`.
        """
        hasher = self.registry.getUtility(IPasswordHasher)
        hashed = hasher.hash_password(password)
        user.hashed_password = hashed

    def verify_password(self, user, password):
        """Validate user password.

        Uses password hasher registered in :py:meth:`websauna.system.Initializer.configure_password`.
        """

        if not user.hashed_password:
            # User password not set, always fail
            return False

        hasher = self.registry.getUtility(IPasswordHasher)
        return hasher.verify_password(user.hashed_password, password)

    def get_by_username(self, username):
        return self.dbsession.query(self.User).filter(func.lower(self.User.username) == username.lower()).first()

    def get_by_email(self, email):
        return self.dbsession.query(self.User).filter(func.lower(self.User.email) == email.lower()).first()

    def get_by_activation(self, activation: object):
        return self.dbsession.query(self.User).filter(self.User.activation_id == activation.id).first()

    def can_login(self, user):
        return user.can_login()

    def get_groups(self, user) -> t.List[GroupMixin]:
        return user.groups

    def create_password_reset_token(self, email) -> t.Optional[t.Tuple[object, str, int]]:
        """Sets password reset token for user.

        :return: [User, password reset token, token expiration in seconds]. ``None`` if user is disabled or is not email login based.
        """
        user = self.get_by_email(email)
        assert user, "Got password reset request for non-existing email".format(email)

        if not self.can_login(user):
            return None

        activation_token_expiry_seconds = int(self.registry.settings.get("websauna.activation_token_expiry_seconds", 24*3600))

        activation = self.Activation()
        activation.expires_at = now() + timedelta(seconds=activation_token_expiry_seconds)
        self.dbsession.add(activation)
        self.dbsession.flush()
        user.activation = activation

        assert user.activation.code, "Could not generate the password reset code"

        return user, activation.code, activation_token_expiry_seconds

    def create_email_activation_token(self, user) -> t.Tuple[str, int]:
        """Create activation token for the user to be used in the email

        :return: Tuple (email activation code, expiration in seconds)
        """
        activation = self.Activation()
        activation_token_expiry_seconds = int(self.registry.settings.get("websauna.activation_token_expiry_seconds", 24*3600))
        activation.expires_at = now() + timedelta(seconds=activation_token_expiry_seconds)

        self.dbsession.add(activation)
        self.dbsession.flush()
        user.activation = activation
        return [activation.code, activation_token_expiry_seconds]

    def get_authenticated_user_by_username(self, username, password) -> t.Optional[UserMixin]:
        """Authenticate incoming user.

        :return: User instance of none if password does not match
        """
        user = self.get_by_username(username)
        if user and self.verify_password(user, password):
            return user
        return None

    def get_authenticated_user_by_email(self, email, password) -> t.Optional[UserMixin]:
        user = self.get_by_email(email)
        if user and self.verify_password(user, password):
            return user
        return None

    def get_session_token(self, user):
        """Get marker string we use to store reference to this user in authenticated session."""
        return user.id

    def get_user_by_session_token(self, token: str):
        """Resolve the authenticated user by a session token reference."""
        return self.dbsession.query(self.User).get(token)

    def get_user_by_password_reset_token(self, token: str):
        """Get user by a password token issued earlier.

        Consume any activation token.
        """
        activation = self.dbsession.query(self.Activation).filter(self.Activation.code == token).first()

        if activation:

            if activation.is_expired():
                return None

            user = self.get_by_activation(activation)
            return user

        return None

    def activate_user_by_email_token(self, token: str):
        """Get user by a password token issued earlier.

        Consume any activation token.
        """
        activation = self.dbsession.query(self.Activation).filter(self.Activation.code == token).first()

        if activation:

            if activation.is_expired():
                return None

            user = self.get_by_activation(activation)
            user.activated_at = now()
            self.dbsession.delete(activation)
            return user

        return None

    def reset_password(self, user: UserMixin, password: str):
        """Reset user password and clear all pending activation issues."""

        self.set_password(user, password)

        if not user.activated_at:
            user.activated_at = now()
        self.dbsession.delete(user.activation)

    def sign_up(self, registration_source: str, user_data: dict) -> UserMixin:
        """Sign up a new user through registration form.

        """

        password = user_data.pop("password", None)

        u = self.User(**user_data)

        if password:
            self.set_password(u, password)

        self.dbsession.add(u)
        self.dbsession.flush()

        # Generate default username (should not be exposed by default)
        u.username = u.generate_username()

        # Record how we created this record
        u.registration_source = registration_source

        self.dbsession.flush()
        return u
