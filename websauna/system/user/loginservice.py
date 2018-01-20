"""Default login service implementation."""
# Pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import forget
from pyramid.security import remember
from pyramid.settings import asbool
from zope.interface import implementer

# Websauna
from websauna.system.core import messages
from websauna.system.core.route import get_config_route
from websauna.system.http import Request
from websauna.system.user.interfaces import ILoginService
from websauna.system.user.interfaces import IUser
from websauna.system.user.usermixin import UserMixin
from websauna.system.user.utils import get_user_registry
from websauna.utils.time import now

from . import events
from .interfaces import AuthenticationFailure


@implementer(ILoginService)
class DefaultLoginService:
    """A login service which tries to authenticate with email and username against the current user registry.

    Login service must know details about user implementation and user registry abstraction is not enough.
    """

    def __init__(self, request: Request):
        """Initialize LoginService.

        :param request: Pyramid Request.
        """
        self.request = request

    def update_login_data(self, user: IUser):
        """Update last_login_at and last_login_ip on User object.

        If this is the User first login, trigger FirstLogin event.

        :param user: User object.
        """
        request = self.request
        if not user.last_login_at:
            e = events.FirstLogin(request, user)
            request.registry.notify(e)

        # Update user security details
        user.last_login_at = now()
        user.last_login_ip = request.client_addr

    def check_credentials(self, username: str, password: str) -> UserMixin:
        """Check if the user password matches.

        * First try username + password
        + Then try with email + password

        :param username: username or email
        :param password:
        :raise websauna.system.user.interfaces.AuthenticationFailure: On login problem.
        :return: User object which was picked
        """
        request = self.request
        settings = request.registry.settings
        allow_email_auth = settings.get('websauna.allow_email_auth', True)

        # Check login with username
        user_registry = get_user_registry(request)
        user = user_registry.get_authenticated_user_by_username(username, password)

        # Check login with email
        if allow_email_auth and not user:
            user = user_registry.get_authenticated_user_by_email(username, password)

        if not user:
            raise AuthenticationFailure('Invalid username or password.')

        return user

    def greet_user(self, user: IUser):
        """Allow easy overriding of a welcome message.

        :param user: User object.
        """
        messages.add(self.request, kind="success", msg="You are now logged in.", msg_id="msg-you-are-logged-in")

    def do_post_login_actions(self, user: IUser, headers: dict, location: str=None) -> Response:
        """What happens after a successful login.

        Override this to customize e.g. where the user lands.

        :param user: User object.
        :param headers: Dictionary with headers to be added to the HTTPFound response.
        :param location: URL to redirect the user to.
        :return: Redirection to location.
        """
        request = self.request

        if not location:
            location = get_config_route(request, 'websauna.login_redirect')

        self.greet_user(user)

        self.update_login_data(user)

        e = events.Login(request, user)
        request.registry.notify(e)

        return HTTPFound(location=location, headers=headers)

    def authenticate_user(self, user: IUser, login_source: str, location: str=None) -> Response:
        """Make the current session logged in session for this particular user.

        How to authenticate user using the login service (assuming you have done password match or related yourself):

        .. code-block:: python

            from websauna.system.user.utils import get_login_service

            def my_view(request):

                # load user model instance from database
                # user = ...

                login_service = get_login_service(request)
                response = login_service.authenticate_user(user, "my-login-source")

        :param user: User object.
        :param login_source: Source of this login.
        :param location: Location to redirect the user to.
        :raise AuthenticationFailure: If login cannot proceed due to disabled user account, etc.
        :return: HTTPResponse what should happen as post-login action
        """
        request = self.request
        settings = request.registry.settings

        require_activation = asbool(settings.get('websauna.require_activation', True))
        allow_inactive_login = asbool(settings.get('websauna.allow_inactive_login', False))

        if (not allow_inactive_login) and require_activation and (not user.is_activated()):
            raise AuthenticationFailure('Your account is not active, please check your e-mail. If your account activation email as expired please request a password reset.')

        if not user.can_login():
            raise AuthenticationFailure('This user account cannot log in at the moment.')

        user_registry = get_user_registry(request)
        token = user_registry.get_session_token(user)
        headers = remember(request, token)
        # assert headers, "Authentication backend did not give us any session headers"

        return self.do_post_login_actions(user, headers, location)

    def authenticate_credentials(self, username: str, password: str, login_source: str, location: str=None) -> Response:
        """Try logging in the user with username and password.

        This is called after the user credentials have been validated, after sign up when direct sign in after sign up is in use or after successful federated authentication.

        Sets the auth cookies and redirects to a post login page, which defaults to a view named 'index'.

        Fills in user last login time and IP data..

        :param username: Username.
        :param password: User password.
        :param login_source: Source of this login attempt.
        :param location: Override the redirect page. If none use ``websauna.login_redirect``. TODO - to be changed.
        :raise: AuthenticationError
        :return: HTTPResponse what should happen as post-login action
        """
        # See that our user model matches one we expect from the configuration
        user = self.check_credentials(username, password)
        return self.authenticate_user(user, login_source, location)

    def logout(self, location: str=None) -> Response:
        """Log out user from the site.

        * Terminate session
        * Show logged out message
        * Redirect the user to post login page

        :param location: Override the redirect page. If none use ``websauna.login_redirect``. TODO - to be changed.
        :return: HTTPFound to location.
        """
        # TODO: Horus might go
        request = self.request
        logout_redirect_view = get_config_route(request, 'websauna.logout_redirect')
        location = location or logout_redirect_view

        messages.add(request, msg="You are now logged out.", kind="success", msg_id="msg-logged-out")
        headers = forget(request)
        return HTTPFound(location=location, headers=headers)
