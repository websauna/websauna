"""User login and sign up handling views.

.. note::

    This is code is blasphemy and will be replaced with something more sane in the future versions. I suggest you just copy-paste this and do from the scratch for your project.
"""

import logging

from datetime import timedelta

from pyramid.session import check_csrf_token

from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPFound, HTTPMethodNotAllowed
from pyramid.httpexceptions import HTTPNotFound
from pyramid.settings import asbool
from pyramid.settings import aslist
from pyramid.renderers import render_to_response

from pyramid_mailer import get_mailer

import deform

from hem.db import get_session


from horus.interfaces import IActivationClass
from horus.interfaces import ILoginForm
from horus.interfaces import ILoginSchema
from horus.interfaces import IRegisterForm
from horus.interfaces import IRegisterSchema
from horus.interfaces import IForgotPasswordForm
from horus.interfaces import IForgotPasswordSchema
from horus.interfaces import IResetPasswordForm
from horus.interfaces import IResetPasswordSchema
from horus.interfaces import IProfileForm
from horus.interfaces import IProfileSchema
from horus.events import NewRegistrationEvent
from horus.events import RegistrationActivatedEvent
from horus.events import PasswordResetEvent
from horus.lib import FlashMessage
from horus.models import _, UserMixin
from horus import views as horus_views
from horus.views import get_config_route
from websauna.system import ILoginService

from websauna.system.mail import send_templated_mail
from websauna.utils.slug import uuid_to_slug, slug_to_uuid
from websauna.system.user.utils import get_user_class, get_site_creator, get_login_service, get_oauth_login_service, get_credential_activity_service
from websauna.system.core import messages
from websauna.utils.time import now
from .interfaces import AuthenticationFailure, CannotResetPasswordException

logger = logging.getLogger(__name__)


def create_activation(request, user):
    """Create through-the-web user sign up with his/her email.

    We don't want to force the users to pick up an usernames, so we just generate an username.
    The user is free to change their username later.
    """

    assert user.id
    user.username = user.generate_username()
    user.registration_source = "email"

    db = get_session(request)
    Activation = request.registry.getUtility(IActivationClass)
    activation = Activation()
    activation_token_expiry_seconds = int(request.registry.settings.get("websauna.activation_token_expiry_seconds", 24*3600))

    activation.expires_at = now() + timedelta(seconds=activation_token_expiry_seconds)

    db.add(activation)
    user.activation = activation

    db.flush()

    # TODO Create a hook for this, don't assume create_activation() call
    # TODO We don't need pystache just for this!
    context = {
        'link': request.route_url('activate', user_id=uuid_to_slug(user.uuid), code=user.activation.code)
    }

    send_templated_mail(request, [user.email], "login/email/activate", context)

    site_creator = get_site_creator(request.registry)
    site_creator.check_empty_site_init(request.dbsession, user)


class RegisterController(horus_views.RegisterController):

    def __init__(self, request):
        super(RegisterController, self).__init__(request)
        schema = request.registry.getUtility(IRegisterSchema)
        self.schema = schema().bind(request=self.request)

        sign_up_button = deform.Button(name="sign_up", title="Sign up with email", css_class="btn-lg btn-block")

        form = request.registry.getUtility(IRegisterForm)
        self.form = form(self.schema, buttons=(sign_up_button,))

        self.after_register_url = route_url(
            self.settings.get('horus.register_redirect', 'index'), request)
        self.after_activate_url = route_url(
            self.settings.get('horus.activate_redirect', 'index'), request)

        self.require_activation = asbool(
            self.settings.get('horus.require_activation', True))

        if self.require_activation:
            self.mailer = get_mailer(request)

        self.login_after_activation = asbool(self.settings.get('horus.login_after_activation', False))

    def waiting_for_activation(self, user):
        return render_to_response('login/waiting_for_activation.html', {"user": user}, request=self.request)

    @view_config(route_name='register', renderer='login/register.html')
    def register(self):

        social_logins = aslist(self.settings.get("websauna.social_logins", ""))

        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.after_register_url)

            return {'form': self.form.render(), 'social_logins': social_logins}

        elif self.request.method != 'POST':
            return

        # If the request is a POST:
        controls = self.request.POST.items()
        try:
            captured = self.form.validate(controls)
        except deform.ValidationFailure as e:
            return {'form': e.render(), 'errors': e.error.children, 'social_logins': social_logins}

        # With the form validated, we know email and username are unique.
        del captured['csrf_token']
        user = self.persist_user(captured)

        autologin = asbool(self.settings.get('horus.autologin', False))

        if self.require_activation:
            self.db.flush()
            create_activation(self.request, user)
        elif not autologin:
            FlashMessage(self.request, self.Str.registration_done,
                         kind='success')

        self.request.registry.notify(NewRegistrationEvent(
            self.request, user, None, controls))
        if autologin:
            self.db.flush()  # in order to get the id
            login_service = get_login_service(self.request.registry)
            return login_service.authenticate(self.request, user)
        else:  # not autologin: user must log in just after registering.
            return self.waiting_for_activation(user)

    @view_config(route_name='activate')
    def activate(self):
        """View to activate user after clicking email link."""

        code = self.request.matchdict.get('code', None)
        user_id = self.request.matchdict.get('user_id', None)
        User = get_user_class(self.request.registry)
        activation = self.Activation.get_by_code(self.request, code)

        if activation and not activation.is_expired():
            user_uuid = slug_to_uuid(user_id)
            user = self.request.dbsession.query(User).filter_by(uuid=user_uuid).first()

            if not user or (user.activation != activation):
                raise HTTPNotFound()

            if user:
                user.activated_at = now()
                self.db.delete(activation)
                self.db.flush()

                if self.login_after_activation:
                    login_service = get_login_service(self.request)
                    return login_service.authenticate_user(user)
                else:
                    self.request.registry.notify(RegistrationActivatedEvent(self.request, user, activation))
                    return HTTPFound(location=self.after_activate_url)

        raise HTTPNotFound()



class AuthController(horus_views.AuthController):

    def __init__(self, request):
        super(AuthController, self).__init__(request)

        schema = request.registry.getUtility(ILoginSchema)
        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(ILoginForm)

        # XXX: Bootstrap classes leak into Deform here
        login_button = deform.Button(name="login_email", title="Login with email", css_class="btn-lg btn-block")
        self.form = form(self.schema, buttons=(login_button,))

        # If the form is embedded on other pages force it go to right HTTP POST endpoint
        self.form.action = request.route_url("login")

    @view_config(route_name='login', renderer='login/login.html')
    def login(self):

        social_logins = aslist(self.settings.get("websauna.social_logins", ""))

        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.login_redirect_view)
            return {'form': self.form.render(), "social_logins": social_logins}

        elif self.request.method == 'POST':

            check_csrf_token(self.request)

            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except deform.ValidationFailure as e:
                return {
                    'form': e.render(),
                    'errors': e.error.children
                }

            username = captured['username']
            password = captured['password']
            login_service = get_login_service(self.request)

            try:
                return login_service.authenticate_credentials(username, password, login_source="login_form")
            except AuthenticationFailure as e:

                # Tell user they cannot login at the moment
                messages.add(self.request, msg=str(e), msg_id="msg-authentication-failure", kind="error")

                return {
                    'form': self.form.render(appstruct=captured),
                    'errors': [e],
                    "social_logins": social_logins
                }


        else:
            raise AssertionError("Unknown HTTP method")

    @view_config(route_name='registration_complete', renderer='login/registration_complete.html')
    def registration_complete(self):
        """After activation initial login screen."""

        self.form.action = self.request.route_url('login')
        return {"form": self.form.render()}

    @view_config(route_name='login_social')
    def login_social(self):
        """Login using OAuth and any of the social providers."""

        # Get the internal provider name URL variable.
        provider_name = self.request.matchdict.get('provider_name')
        oauth_login_service = get_oauth_login_service(self.request)
        return oauth_login_service.handle_request(provider_name)

    @view_config(permission='authenticated', route_name='logout')
    def logout(self):
        # Don't allow <img src="http://server/logout">
        assert self.request.method == "POST"
        check_csrf_token(self.request)
        login_service = get_login_service(self.request)
        return login_service.logout()


class ForgotPasswordController(horus_views.ForgotPasswordController):
    """TODO: This view is going to see a rewrite."""

    @view_config(route_name='forgot_password', renderer='login/forgot_password.html')
    def forgot_password(self):
        req = self.request
        schema = req.registry.getUtility(IForgotPasswordSchema)
        schema = schema().bind(request=req)

        form = req.registry.getUtility(IForgotPasswordForm)
        form = form(schema)

        if req.method == 'GET':
            if req.user:
                return HTTPFound(location=self.forgot_password_redirect_view)
            else:
                return {'form': form.render()}

        # From here on, we know it's a POST. Let's validate the form
        controls = req.POST.items()
        try:
            captured = form.validate(controls)
        except deform.ValidationFailure as e:
            # This catches if the email does not exist, too.
            return {'form': e.render(), 'errors': e.error.children}

        credential_activity_service = get_credential_activity_service(self.request)
        # Process valid form
        email = captured["email"]

        try:
            return credential_activity_service.create_forgot_password_request(email)
        except CannotResetPasswordException as e:
            messages.add(self.request, msg=str(e), msg_id="msg-cannot-reset-password", kind="error")
            return {'form': form.render()}


    @view_config(route_name='reset_password', renderer='login/reset_password.html')
    def reset_password(self):
        """Perform the actual reset based on the email reset link.

        User arrives on the page and enters the new password.
        """
        schema = self.request.registry.getUtility(IResetPasswordSchema)
        schema = schema().bind(request=self.request)

        form = self.request.registry.getUtility(IResetPasswordForm)
        form = form(schema)

        code = self.request.matchdict.get('code', None)
        credential_activity_service = get_credential_activity_service(self.request)
        user = credential_activity_service.get_user_for_password_reset_token(code)
        if not user:
            raise HTTPNotFound("Invalid password reset code")

        if self.request.method == 'GET':
            return {
                'form': form.render(
                    appstruct=dict(
                        user=user.friendly_name
                    )
                )
            }

        elif self.request.method == 'POST':
            try:
                controls = self.request.POST.items()
                captured = form.validate(controls)
            except deform.ValidationFailure as e:
                return {'form': e.render(), 'errors': e.error.children}

            password = captured['password']

            return credential_activity_service.reset_password(code, password)
        else:
            raise HTTPMethodNotAllowed()