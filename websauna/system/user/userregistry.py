"""Default user object generator."""
# Standard Library
import typing as t
from datetime import timedelta

# Pyramid
from zope.interface import implementer

# SQLAlchemy
from sqlalchemy import func

# Websauna
from websauna.system.user.interfaces import IActivationModel
from websauna.system.user.interfaces import IPasswordHasher
from websauna.system.user.interfaces import IUser
from websauna.system.user.interfaces import IUserModel
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
        """Initialize DefaultEmailBasedUserRegistry.

        :param request:Pyramid request.
        """
        self.dbsession = request.dbsession
        self.registry = request.registry

    @property
    def User(self) -> t.Type[IUserModel]:
        """Currently configured User SQLAlchemy model.

        :return: Class implementing IUserModel.
        """
        return get_user_class(self.registry)

    @property
    def Activation(self) -> t.Type[IActivationModel]:
        """Currently configured User SQLAlchemy model.

        :return: Class implementing IActivationModel.
        """
        return get_activation_model(self.registry)

    def set_password(self, user: IUser, password: str):
        """Hash a password for persistent storage.

        Uses password hasher registered in :py:meth:`websauna.system.Initializer.configure_password`.

        :param user: User object.
        :param password: User password.
        """
        hasher = self.registry.getUtility(IPasswordHasher)
        hashed = hasher.hash_password(password)
        user.hashed_password = hashed

    def verify_password(self, user: IUser, password: str) -> bool:
        """Validate user password.

        Uses password hasher registered in :py:meth:`websauna.system.Initializer.configure_password`.

        :param user: User object.
        :param password: User password.
        :return: Boolean of the password verification.
        """
        if not user.hashed_password:
            # User password not set, always fail
            return False

        hasher = self.registry.getUtility(IPasswordHasher)
        return hasher.verify_password(user.hashed_password, password)

    def get_by_username(self, username: str) -> IUser:
        """Return the User with the given username.

        We always compare the lowercase version of User.username and username.

        :param username: Username to be used.
        :return: User object.
        """
        username = username.lower()
        user_class = self.User
        return self.dbsession.query(user_class).filter(func.lower(user_class.username) == username).first()

    def get_by_email(self, email: str) -> IUser:
        """Return the User with the given email.

        We always compare the lowercase version of User.email and email.

        :param email: Email to be used.
        :return: User object.
        """
        email = email.lower()
        user_class = self.User
        return self.dbsession.query(user_class).filter(func.lower(user_class.email) == email).first()

    def get_by_activation(self, activation: IActivationModel) -> IUser:
        """Return the User with the given activation.

        :param activation: Activation object..
        :return: User object.
        """
        user_class = self.User
        return self.dbsession.query(user_class).filter(user_class.activation_id == activation.id).first()

    def can_login(self, user: IUser) -> bool:
        """Verify if user is allowed do login.

        :param user: User object.
        :return: Boolean
        """
        return user.can_login()

    def can_reset_password(self, user: IUser) -> bool:
        """Verify if user is allowed to reset their password.

        :param user: User object.
        :return: Boolean
        """
        return user.enabled

    def get_groups(self, user: IUser) -> t.List[GroupMixin]:
        """Groups for a user.

        :param user: User object.
        :return: List of groups for this user.
        """
        return user.groups

    def create_password_reset_token(self, email: str) -> t.Optional[t.Tuple[object, str, int]]:
        """Sets password reset token for user.

        :param email: Email to be used.
        :return: [User, password reset token, token expiration in seconds]. ``None`` if user is disabled or is not email login based.
        """
        user = self.get_by_email(email)
        assert user, "Got password reset request for non-existing email".format(email)

        if not self.can_reset_password(user):
            return None

        activation_token_expiry_seconds = int(self.registry.settings.get("websauna.activation_token_expiry_seconds", 24 * 3600))

        activation = self.Activation()
        activation.expires_at = now() + timedelta(seconds=activation_token_expiry_seconds)
        self.dbsession.add(activation)
        self.dbsession.flush()
        user.activation = activation

        assert user.activation.code, "Could not generate the password reset code"

        return user, activation.code, activation_token_expiry_seconds

    def create_email_activation_token(self, user: IUser) -> t.Tuple[str, int]:
        """Create activation token for the user to be used in the email

        :param user: User object.
        :return: Tuple (email activation code, expiration in seconds)
        """
        activation = self.Activation()
        activation_token_expiry_seconds = int(self.registry.settings.get("websauna.activation_token_expiry_seconds", 24 * 3600))
        activation.expires_at = now() + timedelta(seconds=activation_token_expiry_seconds)

        self.dbsession.add(activation)
        self.dbsession.flush()
        user.activation = activation
        return activation.code, activation_token_expiry_seconds

    def get_authenticated_user_by_username(self, username: str, password: str) -> t.Optional[UserMixin]:
        """Authenticate incoming user using username and password.

        :param username: Provided username.
        :param password: Provided password.
        :return: User instance of none if password does not match
        """
        user = self.get_by_username(username)
        if user and self.verify_password(user, password):
            return user
        return None

    def get_authenticated_user_by_email(self, email: str, password: str) -> t.Optional[UserMixin]:
        """Authenticate incoming user using email and password.

        :param email: Provided email.
        :param password: Provided password.
        :return: User instance of none if password does not match
        """
        user = self.get_by_email(email)
        if user and self.verify_password(user, password):
            return user
        return None

    def get_session_token(self, user: IUser):
        """Get marker string we use to store reference to this user in authenticated session.

        :param user: User object.
        :return: User id.
        """
        return user.id

    def get_user_by_session_token(self, token: str) -> UserMixin:
        """Resolve the authenticated user by a session token reference.

        :param token: Token to be used to return the user.
        :return: User object.
        """
        return self.dbsession.query(self.User).get(token)

    def get_user_by_password_reset_token(self, token: str) -> t.Optional[UserMixin]:
        """Get user by a password token issued earlier.

        Consume any activation token.

        :param token: Reset password token to be used to return the user.
        :return: User instance of none if token is not found.
        """
        activation = self.dbsession.query(self.Activation).filter(self.Activation.code == token).first()

        if activation:
            if activation.is_expired():
                return None
            user = self.get_by_activation(activation)
            return user
        return None

    def activate_user_by_email_token(self, token: str) -> t.Optional[UserMixin]:
        """Get user by a password token issued earlier.

        Consume any activation token.

        :param token: Password token to be used to return the user.
        :return: User instance of none if token is not found.
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

    def reset_password(self, user: IUser, password: str):
        """Reset user password and clear all pending activation issues.

        :param user: User object,
        :param password: New password.
        """
        self.set_password(user, password)

        if not user.activated_at:
            user.activated_at = now()
        self.dbsession.delete(user.activation)

    def sign_up(self, registration_source: str, user_data: dict) -> UserMixin:
        """Sign up a new user through registration form.

        :param registration_source: Indication where the user came from.
        :param user_data: Payload with new user information.
        :return: Newly created User object.
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
