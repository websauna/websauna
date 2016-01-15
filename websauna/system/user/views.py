"""User login and sign up handling views.

.. note::

    This is code is blasphemy and will be replaced with something more sane in the future versions. I suggest you just copy-paste this and do from the scratch for your project.
"""

import logging

from authomatic.core import LoginResult
from pyramid.session import check_csrf_token

from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.settings import asbool
from pyramid.settings import aslist
from pyramid.renderers import render_to_response
from pyramid.response import Response

from pyramid_mailer import get_mailer

import deform

from hem.db import get_session

from horus.interfaces import IUserClass
from horus.interfaces import IActivationClass
from horus.interfaces import IUIStrings
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
from horus.exceptions import AuthenticationFailure
from horus import views as horus_views
from horus.views import get_config_route

from authomatic.adapters import WebObAdapter
from websauna.system.http import Request

from websauna.system.mail import send_templated_mail
from websauna.utils.slug import uuid_to_slug, slug_to_uuid
from websauna.utils.time import now

from . import events
from websauna.system.user.social import NotSatisfiedWithData
from websauna.system.user.utils import get_authomatic, get_social_login_mapper, get_user_class, get_site_creator
from websauna.system.core import messages


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


def authenticated(request:Request, user:UserMixin, location:str=None) -> HTTPFound:
    """Logs in the user.

    TODO: Make this is a registry component for overriding

    Sets the auth cookies and redirects to the page defined in horus.login_redirect, which defaults to a view named 'index'.

    Fills in user last login details.

    :param request: Current request

    :param user: User model to log in

    :param location: Override the redirect page. If none use ``horus.login_redirect``
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

    if not user.last_login_at:
        e = events.FirstLogin(request, user)
        request.registry.notify(e)

    # Update user security details
    user.last_login_at = now()
    user.last_login_ip = request.client_addr

    if not location:
        location = get_config_route(request, 'horus.login_redirect')

    messages.add(request, kind="success", msg="You are now logged in.", msg_id="msg-you-are-logged-in")

    return HTTPFound(location=location, headers=headers)


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
            return authenticated(self.request, user)
        else:  # not autologin: user must log in just after registering.
            return self.waiting_for_activation(user)

    @view_config(route_name='activate')
    def activate(self):
        """View to activate user after clicking email link."""

        code = self.request.matchdict.get('code', None)
        user_id = self.request.matchdict.get('user_id', None)
        User = get_user_class(self.request.registry)
        activation = self.Activation.get_by_code(self.request, code)

        if activation:
            user_uuid = slug_to_uuid(user_id)
            user = self.request.dbsession.query(User).filter_by(uuid=user_uuid).first()

            if not user or (user.activation != activation):
                return HTTPNotFound()

            if user:
                self.db.delete(activation)
                self.db.flush()

                if self.login_after_activation:
                    return authenticated(self.request, user)
                else:
                    self.request.registry.notify(RegistrationActivatedEvent(self.request, user, activation))
                    return HTTPFound(location=self.after_activate_url)

        return HTTPNotFound()


class AuthController(horus_views.AuthController):

    def __init__(self, request):
        super(AuthController, self).__init__(request)

        schema = request.registry.getUtility(ILoginSchema)
        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(ILoginForm)

        self.login_redirect_view = get_config_route(
            request,
            'horus.login_redirect'
        )

        self.logout_redirect_view = get_config_route(
            request,
            'horus.logout_redirect'
        )

        self.require_activation = asbool(
            self.settings.get('horus.require_activation', True)
        )
        self.allow_inactive_login = asbool(
            self.settings.get('horus.allow_inactive_login', False)
        )

        # XXX: Bootstrap classes leak into Deform here
        login_button = deform.Button(name="login_email", title="Login with email", css_class="btn-lg btn-block")
        self.form = form(self.schema, buttons=(login_button,))

        # If the form is embedded on other pages force it go to right HTTP POST endpoint
        self.form.action = request.route_url("login")

    def check_credentials(self, username, password):
        allow_email_auth = self.settings.get('horus.allow_email_auth', False)

        # Check login with username
        User = get_user_class(self.request.registry)
        user = User.get_user(self.request, username, password)

        # Check login with email
        if allow_email_auth and not user:
            user = User.get_by_email_password(self.request, username, password)

        if not user:
            raise AuthenticationFailure(_('Invalid username or password.'))

        if not self.allow_inactive_login and self.require_activation \
                and not user.is_activated:
            raise AuthenticationFailure(
                _('Your account is not active, please check your e-mail.'))

        if not user.can_login():
            raise AuthenticationFailure(_('This user account cannot log in at the moment.'))

        return user

    @view_config(route_name='login', renderer='login/login.html')
    def login(self):

        social_logins = aslist(self.settings.get("websauna.social_logins", ""))

        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.login_redirect_view)
            return {'form': self.form.render(), "social_logins": social_logins}

        elif self.request.method == 'POST':
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

            try:
                user = self.check_credentials(username, password)
                assert user.password
            except AuthenticationFailure as e:

                # Tell user they cannot login at the moment
                messages.add(self.request, msg=str(e), msg_id="msg-authentication-failure", kind="error")

                return {
                    'form': self.form.render(appstruct=captured),
                    'errors': [e],
                    "social_logins": social_logins
                }

            return authenticated(self.request, user)

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
        ae = AuthomaticLoginHandler(self.request, provider_name)
        response = ae.handle()
        return response

    @view_config(permission='authenticated', route_name='logout')
    def logout(self):
        # Don't allow <img src="http://server/logout">
        assert self.request.method == "POST"
        check_csrf_token(self.request)
        self.request.session.invalidate()
        messages.add(self.request, msg="You are now logged out.", kind="success", msg_id="msg-logged-out")
        headers = forget(self.request)
        return HTTPFound(location=self.logout_redirect_view, headers=headers)


class ForgotPasswordController(horus_views.ForgotPasswordController):

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

        user = self.User.get_by_email(req, captured['email'])
        activation = self.Activation()
        self.db.add(activation)
        self.db.flush()
        user.activation = activation

        assert user.activation.code, "Could not generate the password reset code"
        link = req.route_url('reset_password', code=user.activation.code)

        context = dict(link=link, user=user)
        send_templated_mail(req, [user.email], "login/email/forgot_password", context=context)

        FlashMessage(req, "Please check your email to continue password reset.", kind='success')
        return HTTPFound(location=self.reset_password_redirect_view)

    @view_config(route_name='reset_password', renderer='login/reset_password.html')
    def reset_password(self):
        schema = self.request.registry.getUtility(IResetPasswordSchema)
        schema = schema().bind(request=self.request)

        form = self.request.registry.getUtility(IResetPasswordForm)
        form = form(schema)

        code = self.request.matchdict.get('code', None)

        activation = self.Activation.get_by_code(self.request, code)

        if activation:
            user = self.User.get_by_activation(self.request, activation)

            if user:
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

                    user.password = password
                    self.db.add(user)
                    self.db.delete(activation)

                    FlashMessage(self.request, "The password reset complete. Please sign in with your new password.", kind='success')
                    self.request.registry.notify(PasswordResetEvent(self.request, user, password))
                    location = self.reset_password_redirect_view
                    return HTTPFound(location=location)
        raise HTTPNotFound("Activation code not found")



class AuthomaticLoginHandler:
    """Social login (OAuth/authomatic) internal handling.

   Subclass and override this for customizations.

    Internal implementation of handling OAuth endpoint. The request must be processed as view /login/{provider_name} where provider_name is one of the Authomatic providers set up by Initializer.configure_authomatic(). This view will

    * Check if the request is internal login request and then redirect to OAuth provider

    * Process POST/redirect back from the OAuth Provider

    * Call ISocialAuthMapper to create the user account for incoming social login

    The function returns a tuple. If login success, HTTP response is set. If login fails automatic result is set. If the automatic result is set you are expected to render a login page with error message on it.

    :return: Tuple (HTTP response, Authomatic result)
    """

    def __init__(self, request:Request, provider_name:str):

        self.request = request
        self.provider_name = provider_name

        settings = request.registry.settings
        self.social_logins = aslist(settings.get("websauna.social_logins", ""))

        # Allow only logins which we are configured
        assert provider_name in self.social_logins, "Attempt to login non-configured social media {}".format(provider_name)

        self.mapper = get_social_login_mapper(request.registry, provider_name)
        assert self.mapper, "No social media login mapper configured for {}".format(provider_name)

    def process_form(self):
        """Process form values from the internal post request.

        By default this doesn nothing. If your site wants to combine e.g. login + choose product action to single POST you can do it here.

        Example::

            class TreesAuthomaticLoginHandler(AuthomaticLoginHandler):

                def process_form(self):
                    request = self.request
                    product_id = request.POST.get("product_id")
                    if product_id:
                        request.session["delivery_data"] = {
                            "product": product_id,
                            "delivery_details": {},
                            "started": now().isoformat()
                        }
                        request.session.changed()


        """

    def do_success(self, authomatic_result:LoginResult) -> Response:
        """Handle we got a valid OAuth login data."""
        user = self.mapper.capture_social_media_user(self.request, authomatic_result)
        return authenticated(self.request, user)

    def do_error(self, authomatic_result: LoginResult, e: Exception) -> Response:
        """Handle getting error from OAuth provider."""
        # We got some error result, now let see how it goes
        request = self.request

        # TODO: Not sure if we shoul log this or now
        logger.exception(e)

        messages.add(self.request, kind="error", msg=str(e), msg_id="authomatic-login-error")

        login_url = self.request.route_url("login")
        return HTTPFound(location=login_url)

    def do_bad_request(self):
        """Handle getting HTTP GET to POST endpoint.

        GoogleBot et. al.
        """
        login_url = self.request.route_url("login")
        return HTTPFound(location=login_url)

    def handle(self) -> Response:

        # Login is always state changing operation
        if self.request.method != 'POST' and not self.request.params:
            self.do_bad_request()

        # We will need the response to pass it to the WebObAdapter.
        response = Response()

        # Get handle to Authomatic instance
        authomatic = get_authomatic(self.request.registry)

        # Start the login procedure.
        class InternalPOSTWebObAdapter(WebObAdapter):
            """Our own request.POST parameters with CSRF would mess up the FB login logic... don't pass them forward."""
            @property
            def params(self):
                return dict()

        if "csrf_token" in self.request.POST:
            # This was internal HTTP POST by our own site to this view
            # TODO: Make it use to explicit post parameter to detect this
            self.process_form()
            adapter = InternalPOSTWebObAdapter(self.request, response)
        else:
            adapter = WebObAdapter(self.request, response)

        authomatic_result = authomatic.login(adapter, self.provider_name)

        if not authomatic_result:
            # Guess it wants to redirect us to Facebook et. al and it set response through the adapter
            return response

        # Grab exception if we get any
        e = None

        if not authomatic_result.error:
            # Login succeeded
            try:
                return self.do_success(authomatic_result)
            except NotSatisfiedWithData as ex:
                # TODO: Clean this up - some scoping issues?
                authomatic_result.error = ex
                e = ex

        return self.do_error(authomatic_result, e)

