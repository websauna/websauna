from horus.views import BaseController

from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.settings import asbool
from pyramid.renderers import render_to_response

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

from horus.views import authenticated

from ..mail import send_templated_mail
from .. import models


def create_activation(request, user):
    """Create through-the-web user sign up with his/her email.

    We don't want to force the users to pick up an usernames, so we just generate an username.
    The user is free to change their username later.
    """

    assert user.id
    user.username = "user-{}".format(user.id)
    user.user_registration_source = models.User.REGISTRATION_SOURCE_EMAIL

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


def authenticate(request, user):
    """Sets the auth cookies and redirects to the page defined in horus.login_redirect, which defaults to a view named 'index'.

    Fills in user last login details.
    """

    assert isinstance(user, models.User)
    assert user.id, "Cannot login with invalid user object"

    settings = request.registry.settings
    headers = remember(request, user.id)
    autologin = asbool(settings.get('horus.autologin', False))

    if not autologin:
        Str = request.registry.getUtility(IUIStrings)
        FlashMessage(request, Str.authenticated, kind='success')

    # Update user security details
    user.last_login_at = datetime.datetime.utcnow()
    user.last_login_ip = request.client_addr

    location = get_config_route(request, 'horus.login_redirect')

    return HTTPFound(location=location, headers=headers)


class RegisterController(BaseController):

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
        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.after_register_url)
            return {'form': self.form.render()}
        elif self.request.method != 'POST':
            return

        # If the request is a POST:
        controls = self.request.POST.items()
        try:
            captured = self.form.validate(controls)
        except deform.ValidationFailure as e:
            return {'form': e.render(), 'errors': e.error.children}

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

    def persist_user(self, controls):
        '''To change how the user is stored, override this method.'''
        # This generic method must work with any custom User class and any
        # custom registration form:
        user = self.User(**controls)
        self.db.add(user)
        return user

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
                FlashMessage(self.request, self.Str.activation_email_verified,
                             kind='success')
                self.request.registry.notify(
                    RegistrationActivatedEvent(self.request, user, activation))
                return HTTPFound(location=self.after_activate_url)
        return HTTPNotFound()


class AuthController(BaseController):

    @view_config(route_name='login', renderer='login/login.html')
    def login(self):
        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.login_redirect_view)
            return {'form': self.form.render()}

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
            except AuthenticationFailure as e:
                FlashMessage(self.request, str(e), kind='error')
                return {
                    'form': self.form.render(appstruct=captured),
                    'errors': [e]
                }

            self.request.user = user  # Please keep this line, my app needs it

            return authenticated(self.request, user.id_value)

