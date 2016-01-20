import zope
from pyramid.interfaces import IRequest, IResponse

from zope.interface import Interface


class IUser(Interface):
    """User.

    Usually SQLAlchemy model instance of :py:class:`websauna.system.user.usermixin.UserMixin`.

    Hard requirements for User interface listed here - this is what Websauna default frontend expects from an user instance.
    """


    #: How we present the user's name to the user itself. Usually. Picks one of 1) full name if set 2) username if set 3) email.
    friendly_name = zope.interface.Attribute("friendly_name")

    #: True if the user has completed email activation or any other external activation required for login
    is_activated = zope.interface.Attribute("is_activated")

    def can_login() -> bool:
        """Can user login.

        True if user is enabled and there is no managerial reason to deny the login.
        """

    def get_session_remember_token() -> str:
        """The token used to carry logged in user in the session.

        Usually just user.id.
        """


class IGroup(Interface):
    """User group.

    Usually SQLAlchemy model instance of :py:class:`websauna.system.user.usermixin.GroupMixin` but can be any object.
    """

    #: Then name of the group
    name = zope.interface.Attribute("name")


class IUserModel(Interface):
    """Register utility registration which marks active User SQLAlchemy model."""


class IGroupModel(Interface):
    """Register utility registration which marks active Group SQLAlchemy model."""

class IActivationModel(Interface):
    """Register utility registration which marks active Activation SQLAlchemy model."""


class IAuthomatic(Interface):
    """Mark Authomatic instance in the registry."""


class ISocialLoginMapper(Interface):
    """Named marker interface to look up social login mappers."""


class ISiteCreator(Interface):
    """Utility that is responsible to create the initial site."""


class AuthenticationFailure(Exception):
    """The user is not allowed to log in."""


class ILoginService(Interface):
    """A service that is responsible for handling normal website facing log in actions.

    This service is responsible to

    * Set up logged in session

    * Do post login actions like redirects

    Use :py:func:`websauna.system.user.utils.get_login_service` to get access to configured login service.
    """

    def authentication_user(user: IUser, login_source:str, location: str=None) -> IResponse:
        """Make the current session logged in session for this particular user.

        A password check is not performed. However it is checked if user is active and such.

        :param location: Override the redirect page. If none use ``horus.login_redirect``. TODO - to be changed.

        :param login_source: Application specific string telling where the login come from. E.g. "social_media", "signup", "login_form".

        :raise AuthenticationFailure: If the user is disabled
        """

    def authenticate_credentials(username: str, login_source:str, password: str, location: str=None) -> IResponse:
        """Logs in the user.

        This is called after the user credentials have been validated.

        Sets the auth cookies and redirects to a post login page, which defaults to a view named 'index'.

        Fills in user last login time and IP data..

        :param request: Current request

        :param user: Default login service is designed to work with UserMixin compatible user classes

        :param location: Override the redirect page. If none use ``horus.login_redirect``. TODO - to be changed.

        :param login_source: Application specific string telling where the login come from. E.g. "social_media", "signup", "login_form".

        :raise AuthenticationFailure: If the password does not match or user is disabled
        """

    def logout(location:str =None) -> IResponse:
        """Log out user from the site.

        * Terminate session

        * Show logged out message

        * Redirect the user to post login page
        """


class IOAuthLoginService(Interface):
    """A login service for federated authentication.

    See :py:class:`websauna.system.interfaces.ILoginService`.

    Use :py:func:`websauna.system.user.utils.get_oauth_login_service` to get access to configured login service.
    """

    def handle_request(provider_name: str) -> IResponse:
        """Handle all requests coming to login/facebook, login/twitter etc. endpoints.

        * Login form does an empty HTTP POST request to initiate OAuth process

        * Federated authentication service does HTTP GET redirect when they accept OAuth authentication request
        """


class IUserRegistry(Interface):
    """Manage creation and querying of users.

    Allow abstraction over the user backend - do not assume users are stored in the primary database.
    """


class CannotResetPasswordException(Exception):
    pass


class ICredentialActivityService(Interface):
    """User password and activation related activities."""

