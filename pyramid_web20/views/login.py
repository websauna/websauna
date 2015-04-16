import datetime
import transaction

from horus.views import BaseController

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
from pyramid_mailer.message import Message

import deform
import deform.widget as w
import colander as c

from hem.db import get_session
from hem.schemas import CSRFSchema

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
from horus.events import ProfileUpdatedEvent
from horus.lib import FlashMessage
from horus.models import _
from horus.exceptions import AuthenticationFailure
from horus.httpexceptions import HTTPBadRequest
from horus import views as horus_views
from horus.views import get_config_route

from authomatic.adapters import WebObAdapter

from ..mail import send_templated_mail
from .. import models
from .. import authomatic


class NotSatisfiedWithData(Exception):
    """Risen when social media login cannot proceed due to incomplete provided information."""


def create_activation(request, user):
    """Create through-the-web user sign up with his/her email.

    We don't want to force the users to pick up an usernames, so we just generate an username.
    The user is free to change their username later.
    """

    assert user.id
    user.username = user.generate_username()
    user.user_registration_source = models.UserMixin.USER_MEDIA_EMAIL

    db = get_session(request)
    Activation = request.registry.getUtility(IActivationClass)
    activation = Activation()

    db.add(activation)
    user.activation = activation

    db.flush()

    # TODO Create a hook for the app to give us body and subject!
    # TODO We don't need pystache just for this!
    context = {
        'link': request.route_url('activate', user_id=user.id,
                                  code=user.activation.code)
    }

    send_templated_mail(request, [user.email], "login/email/activate", context)

    models.check_empty_site_init(user)


def authenticated(request, user):
    """Sets the auth cookies and redirects to the page defined in horus.login_redirect, which defaults to a view named 'index'.

    Fills in user last login details.
    """

    # See that our user model matches one we expect from the configuration
    registry = request.registry
    User = registry.queryUtility(IUserClass)
    assert User
    assert isinstance(user, User)

    assert user.id, "Cannot login with invalid user object"
    if not user.can_login():
        raise RuntimeError("Got authenticated() request for disabled user - should not happen")

    headers = remember(request, user.id)
    assert headers, "Authentication backend did not give us any session headers"

    # Update user security details
    user.last_login_at = datetime.datetime.utcnow()
    user.last_login_ip = request.client_addr

    location = get_config_route(request, 'horus.login_redirect')

    user.first_login = False

    return HTTPFound(location=location, headers=headers)


def normalize_facebook_data(data):
    return {
        "country": data.country,
        "timezone": data.timezone,
        "gender": data.gender,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "full_name": data.first_name + " " + data.last_name,
        "link": data.link,
        "birth_date": data.birth_date,
        "city": data.city,
        "postal_code": data.postal_code,
        "email": data.email,
        "id": data.id,
        "nickname": data.nickname,
    }


def update_first_login_social_data(user, data):
    """
    :param data: Normalized data
    """
    if not user.full_name and data.get("full_name"):
        user.full_name = data["full_name"]


def get_or_create_user_by_social_medial_email(request, provider, email, social_data):
    """ """

    registry = request.registry
    User = registry.queryUtility(IUserClass)

    session = models.DBSession

    user = session.query(User).filter_by(email=email).first()

    if not user:
        user = User(email=email)
        session.add(user)
        session.flush()
        user.username = user.generate_username()
        user.user_registration_source = provider

    if provider == "facebook":
        exported_data = normalize_facebook_data(social_data)
    else:
        raise AssertionError("Unsupported social provider")

    # Update the social network data
    user.social[provider] = exported_data

    if user.first_login:
        update_first_login_social_data(user, exported_data)

    return user


def capture_social_media_user(request, provider, result):
    """Extract social media information from the login in order to associate the user account."""
    assert not result.error

    session = models.DBSession

    if provider == "facebook":
        result.user.update()

        assert result.user.credentials
        assert result.user.id

        if not result.user.email:
            raise NotSatisfiedWithData("Email address is needed in order to user this service and we could not get one from your social media provider. Please try to sign up with your email instead.")

        user = get_or_create_user_by_social_medial_email(request, provider, result.user.email, result.user)

        # Cancel any pending email activations if the user chooses the option to use social media login
        if user.activation:
            session.delete(user.activation)

        models.check_empty_site_init(user)

    return user


class RegisterController(horus_views.RegisterController):

    def __init__(self, request):
        super(RegisterController, self).__init__(request)
        schema = request.registry.getUtility(IRegisterSchema)
        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(IRegisterForm)
        self.form = form(self.schema)

        self.after_register_url = route_url(
            self.settings.get('horus.register_redirect', 'index'), request)
        self.after_activate_url = route_url(
            self.settings.get('horus.activate_redirect', 'index'), request)

        self.require_activation = asbool(
            self.settings.get('horus.require_activation', True))

        if self.require_activation:
            self.mailer = get_mailer(request)

    def waiting_for_activation(self, user):
        return render_to_response('login/waiting_for_activation.html', {"user": user}, request=self.request)

    @view_config(route_name='register', renderer='login/register.html')
    def register(self):

        social_logins = aslist(self.settings.get("pyramid_web20.social_logins", ""))

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
        code = self.request.matchdict.get('code', None)
        user_id = self.request.matchdict.get('user_id', None)

        activation = self.Activation.get_by_code(self.request, code)

        if activation:
            user = self.User.get_by_id(self.request, user_id)

            if user.activation != activation:
                return HTTPNotFound()

            if user:
                self.db.delete(activation)
                # self.db.add(user)  # not necessary
                self.db.flush()

                self.request.registry.notify(
                    RegistrationActivatedEvent(self.request, user, activation))
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

        self.form = form(self.schema, buttons=(self.Str.login_button,))

        # If the form is embedded on other pages force it go to right HTTP POST endpoint
        self.form.action = request.route_url("login")

    def check_credentials(self, username, password):
        allow_email_auth = self.settings.get('horus.allow_email_auth', False)

        user = self.User.get_user(self.request, username, password)

        if allow_email_auth and not user:
            user = self.User.get_by_email_password(
                self.request, username, password)

        if not user:
            raise AuthenticationFailure(_('Invalid username or password.'))

        if not self.allow_inactive_login and self.require_activation \
                and not user.is_activated:
            raise AuthenticationFailure(
                _('Your account is not active, please check your e-mail.'))

        if not user.can_login():
            raise AuthenticationFailure(
                _('Account log in disabled.'))

        return user

    @view_config(route_name='login', renderer='login/login.html')
    def login(self):

        social_logins = aslist(self.settings.get("pyramid_web20.social_logins", ""))

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
                FlashMessage(self.request, str(e), kind='error')
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

    def grab_facebook_data(self, result):
        """Update the user Facebook data field."""
        # We will access the user's 5 most recent statuses.
        url = 'https://graph.facebook.com/{0}?fields=feed.limit(5)'
        url = url.format(result.user.id)

        # Access user's protected resource.
        access_response = result.provider.access(url)

        if access_response.status == 200:
            # Parse response.
            statuses = access_response.data.get('feed').get('data')
            error = access_response.data.get('error')

            if error:
                response.write(u'Damn that error: {0}!'.format(error))
            elif statuses:
                response.write('Your 5 most recent statuses:<br />')
                for message in statuses:

                    text = message.get('message')
                    date = message.get('created_time')

                    response.write(u'<h3>{0}</h3>'.format(text))
                    response.write(u'Posted on: {0}'.format(date))

    @view_config(route_name='login_social')
    def login_social(self):
        """After activation initial login screen."""

        # Login is always state changing operation
        if self.request.method != 'POST' and not self.request.params:
            login_url = self.request.route_url("login")
            return HTTPFound(location=login_url)

        # We will need the response to pass it to the WebObAdapter.
        response = Response()

        social_logins = aslist(self.settings.get("pyramid_web20.social_logins", ""))

        # Get the internal provider name URL variable.
        provider_name = self.request.matchdict.get('provider_name')

        # Allow only logins which we are configured
        if provider_name not in social_logins:
            raise RuntimeError("Attempt to login non-configured social media {}".format(provider_name))

        autho = authomatic.get()

        # Start the login procedure.
        adapter = WebObAdapter(self.request, response)

        authomatic_result = autho.login(adapter, provider_name)

        if not authomatic_result:
            # Guess it wants to redirect us
            return response

        if not authomatic_result.error:
            # Login succeeded
            try:
                user = capture_social_media_user(self.request, provider_name, authomatic_result)
                return authenticated(self.request, user)
            except NotSatisfiedWithData as e:
                # TODO: Clean this up
                authomatic_result.error = e

        # We got some result, now let see how it goes
        self.form.action = self.request.route_url('login')
        context = {"form": self.form.render(), "authomatic_result": authomatic_result, "social_logins": social_logins}
        return render_to_response('login/login.html', context, request=self.request)


