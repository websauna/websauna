"""Default login service implementation."""
from horus.exceptions import AuthenticationFailure
from horus.views import get_config_route
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import remember, forget
from pyramid.settings import asbool
from websauna.system.core import messages
from websauna.system.http import Request
from websauna.system.user.usermixin import UserMixin
from websauna.utils.time import now
from zope.interface import implementer

from websauna.system.user.interfaces import ILoginService, IUser
from websauna.system.user.utils import get_user_class, get_login_service

from . import events


@implementer(ILoginService)
class DefaultLoginService:

    def update_login_data(self, request, user):
        if not user.last_login_at:
            e = events.FirstLogin(request, user)
            request.registry.notify(e)

        # Update user security details
        user.last_login_at = now()
        user.last_login_ip = request.client_addr

    def check_credentials(self, request: Request, username: str, password: str) -> UserMixin:
        """Check if the user password matches.

        :param username: username or email
        :param password:
        :raise horus.exceptionsAuthenticationFailure: On login problem. TODO: Exception class to be changed.
        :return: User object which was picked
        """
        settings = request.registry.settings
        allow_email_auth = settings.get('horus.allow_email_auth', False)

        require_activation = asbool(settings.get('horus.require_activation', True))
        allow_inactive_login = asbool(settings.get('horus.allow_inactive_login', False))
        # Check login with username
        User = get_user_class(request.registry)
        user = User.get_user(request, username, password)

        # Check login with email
        if allow_email_auth and not user:
            user = User.get_by_email_password(request, username, password)

        if not user:
            raise AuthenticationFailure('Invalid username or password.')

        if (not allow_inactive_login) and require_activation and (not user.is_activated):
            raise AuthenticationFailure('Your account is not active, please check your e-mail.')

        if not user.can_login():
            raise AuthenticationFailure('This user account cannot log in at the moment.')

        return user

    def authenticate(self, request: Request, user: UserMixin, location: str=None) -> Response:
        """Logs in the user.

        This is called after the user credentials have been validated, after sign up when direct sign in after sign up is in use or after successful federated authentication.

        Sets the auth cookies and redirects to a post login page, which defaults to a view named 'index'.

        Fills in user last login time and IP data..

        :param request: Current request

        :param user: Default login service is designed to work with UserMixin compatible user classes

        :param location: Override the redirect page. If none use ``horus.login_redirect``. TODO - to be changed.
        """

        # See that our user model matches one we expect from the configuration
        registry = request.registry
        User = get_user_class(registry)
        assert User
        assert isinstance(user, User)

        assert user.id, "Cannot login with invalid user object"
        if not user.can_login():
            raise RuntimeError("Got authenticated() request for disabled user - should not happen")

        headers = remember(request, user.id)
        # assert headers, "Authentication backend did not give us any session headers"

        self.update_login_data(request, user)

        if not location:
            location = get_config_route(request, 'horus.login_redirect')

        messages.add(request, kind="success", msg="You are now logged in.", msg_id="msg-you-are-logged-in")

        return HTTPFound(location=location, headers=headers)

    def logout(self, request: Request, location=None) -> Response:
        """Log out user from the site.

        * Terminate session

        * Show logged out message

        * Redirect the user to post login page
        """

        # TODO: Horus might go
        logout_redirect_view = get_config_route(request, 'horus.logout_redirect')
        location = location or logout_redirect_view

        messages.add(request, msg="You are now logged out.", kind="success", msg_id="msg-logged-out")
        headers = forget(request)
        return HTTPFound(location=location, headers=headers)


