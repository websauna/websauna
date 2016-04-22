"""Sign up form service."""
import logging

from zope.interface import implementer
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.settings import asbool

from websauna.system.core import messages
from websauna.system.http import Request
from websauna.system.mail import send_templated_mail
from websauna.system.user.events import UserCreated
from websauna.system.user.interfaces import IUser, IRegistrationService
from websauna.system.user.utils import get_user_registry, get_login_service

from .events import NewRegistrationEvent, RegistrationActivatedEvent


logger = logging.getLogger(__name__)


@implementer(IRegistrationService)
class DefaultRegistrationService:
    """Default sign up mechanism.

    Send activation email to everybody and ask them to click a link there.
    """

    def __init__(self, request: Request):
        self.request = request

    def sign_up(self, user_data: dict) -> Response:
        """Sign up a new user."""

        user_registry = get_user_registry(self.request)
        user = user_registry.sign_up(registration_source="email", user_data=user_data)

        # Notify site creator to initialize the admin for the first user
        self.request.registry.notify(UserCreated(self.request, user))

        settings = self.request.registry.settings

        require_activation = asbool(settings.get('websauna.require_activation', True))
        autologin = asbool(settings.get('websauna.autologin', False))

        if require_activation:
            self.create_email_activation(user)
        elif not autologin:
            messages.add(self.request, msg_id="msg-sign-up-complete", msg="Sign up complete. Welcome!", kind="success")

        self.request.registry.notify(NewRegistrationEvent(self.request, user, None, user_data))

        self.request.dbsession.flush()  # in order to get the id
        if autologin:
            login_service = get_login_service(self.request.registry)
            return login_service.authenticate(self.request, user)
        else:  # not autologin: user must log in just after registering.
            return render_to_response('login/waiting_for_activation.html', {"user": user}, request=self.request)

    def create_email_activation(self, user: IUser):
        """Create through-the-web user sign up with his/her email.

        We don't want to force the users to pick up an usernames, so we just generate an username.
        The user is free to change their username later.
        """

        user_registry = get_user_registry(self.request)
        activation_code, expiration_seconds = user_registry.create_email_activation_token(user)

        context = {
            'link': self.request.route_url('activate', code=activation_code),
            'expiration_hours': int(expiration_seconds/3600),
        }

        logger.info("Sending sign up email to %s", user.email)

        # TODO: Broken abstraction, we assume user.email is a attribute
        send_templated_mail(self.request, [user.email], "login/email/activate", context)

    def activate_by_email(self, activation_code: str, location=None) -> Response:
        """Active a user after user after the activation email.

        * User clicks link in the activation email

        * User enters the activation code on the form by hand
        """

        request = self.request
        settings = request.registry.settings
        user_registry = get_user_registry(request)

        after_activate_url = request.route_url(settings.get('websauna.activate_redirect', 'index'))
        login_after_activation = asbool(settings.get('websauna.login_after_activation', False))

        user = user_registry.activate_user_by_email_token(activation_code)
        if not user:
            raise HTTPNotFound("Activation code not found")

        if login_after_activation:
            login_service = get_login_service(self.request.registry)
            return login_service.authenticate(self.request, user)
        else:
            self.request.registry.notify(RegistrationActivatedEvent(self.request, user, None))
            return HTTPFound(location=location or after_activate_url)
