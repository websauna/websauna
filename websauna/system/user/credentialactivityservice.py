from horus.views import get_config_route
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from websauna.system.core import messages
from websauna.system.http import Request
from websauna.system.mail import send_templated_mail
from websauna.system.user.interfaces import ICredentialActivityService, CannotResetPasswordException
from websauna.system.user.utils import get_user_registry
from zope.interface import implementer


@implementer(ICredentialActivityService)
class DefaultCredentialActivityService:

    def __init__(self, request: Request):
        self.request = request

    def create_forgot_password_request(self, email, location=None) -> Response:
        """Create a new email activation token for a user and produce the following screen.

        * Sets user password reset token

        * Sends out reset password email

        * The existing of user with such email should be validated beforehand

        :raise: CannotResetPasswordException if there is any reason the password cannot be reset. Usually wrong email.
        """

        request = self.request
        dbsession = self.request.dbsession

        user_registry = get_user_registry(request)

        reset_info = user_registry.create_password_reset_token(email)
        if not reset_info:
            raise CannotResetPasswordException("Cannot reset password for email: {}".format(email))
        user, token = reset_info

        link = request.route_url('reset_password', code=token)
        context = dict(link=link, user=user)
        send_templated_mail(request, [email,], "login/email/forgot_password", context=context)

        messages.add(request, msg="Please check your email to continue password reset.", kind='success', msg_id="msg-check-email")

        if not location:
            location = get_config_route(request, 'horus.reset_password_redirect')
            assert location

        return HTTPFound(location=location)
