"""Password reset."""
# Pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from zope.interface import implementer

# Websauna
from websauna.system.core import messages
from websauna.system.core.route import get_config_route
from websauna.system.http import Request
from websauna.system.mail import send_templated_mail
from websauna.system.user.events import PasswordResetEvent
from websauna.system.user.events import UserAuthSensitiveOperation
from websauna.system.user.interfaces import CannotResetPasswordException
from websauna.system.user.interfaces import ICredentialActivityService
from websauna.system.user.interfaces import IUser
from websauna.system.user.utils import get_user_registry


@implementer(ICredentialActivityService)
class DefaultCredentialActivityService:
    """Handle password reset process and such."""

    def __init__(self, request: Request):
        self.request = request

    def create_forgot_password_request(self, email: str, location: str=None) -> Response:
        """Create a new email activation token for a user and produce the following screen.

        * Sets user password reset token
        * Sends out reset password email
        * The existing of user with such email should be validated beforehand

        :param email: User email.
        :param location: URL to redirect the user after the password request.
        :return: Redirect to location.
        :raise: CannotResetPasswordException if there is any reason the password cannot be reset. Usually wrong email.
        """
        request = self.request

        user_registry = get_user_registry(request)

        reset_info = user_registry.create_password_reset_token(email)
        if not reset_info:
            raise CannotResetPasswordException("Cannot reset password for email: {email}".format(email=email))
        user, token, expiration_seconds = reset_info

        link = request.route_url('reset_password', code=token)
        context = dict(link=link, user=user, expiration_hours=int(expiration_seconds / 3600))
        send_templated_mail(request, [email, ], "login/email/forgot_password", context=context)

        messages.add(request, msg="Please check your email to continue password reset.", kind='success', msg_id="msg-check-email")

        if not location:
            location = get_config_route(request, 'websauna.request_password_reset_redirect')
            assert location

        return HTTPFound(location=location)

    def get_user_for_password_reset_token(self, activation_code: str) -> IUser:
        """Get a user by activation token.

        :param activation_code: User activation code.
        :return: User for the given activation_code.
        """
        request = self.request
        user_registry = get_user_registry(request)
        user = user_registry.get_user_by_password_reset_token(activation_code)
        return user

    def reset_password(self, activation_code: str, password: str, location: str=None) -> Response:
        """Perform actual password reset operations.

        User has following password reset link (GET) or enters the code on a form.

        :param activation_code: Activation code provided by the user.
        :param password: New user password.
        :param location: URL to redirect the user after the password request.
        :return: Redirect to location.
        :raise: HTTPNotFound if activation_code is not found.
        """
        request = self.request
        user_registry = get_user_registry(request)
        user = user_registry.get_user_by_password_reset_token(activation_code)
        if not user:
            return HTTPNotFound("Activation code not found")

        user_registry.reset_password(user, password)

        messages.add(request, msg="The password reset complete. Please sign in with your new password.", kind='success', msg_id="msg-password-reset-complete")

        request.registry.notify(PasswordResetEvent(self.request, user, password))
        request.registry.notify(UserAuthSensitiveOperation(self.request, user, "password_reset"), request)

        location = location or get_config_route(request, 'websauna.reset_password_redirect')
        return HTTPFound(location=location)
