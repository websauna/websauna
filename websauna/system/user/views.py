"""User login and sign up handling views.


.. note ::

    Plan to move something more flexible in the future from these hardcoded, not very feature rich or flexible, views.

"""

import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPMethodNotAllowed
from pyramid.httpexceptions import HTTPNotFound
from pyramid.settings import aslist
import deform

from websauna.system.core import messages
from websauna.system.core.route import get_config_route
from websauna.system.http import Request
from .utils import get_login_service, get_oauth_login_service, get_credential_activity_service, get_registration_service
from .interfaces import AuthenticationFailure, CannotResetPasswordException
from .interfaces import ILoginForm
from .interfaces import ILoginSchema
from .interfaces import IRegisterForm
from .interfaces import IRegisterSchema
from .interfaces import IForgotPasswordForm
from .interfaces import IForgotPasswordSchema
from .interfaces import IResetPasswordForm
from .interfaces import IResetPasswordSchema

logger = logging.getLogger(__name__)


@view_config(route_name='register', renderer='login/register.html')
def register(request: Request):
    """Sign up view."""

    settings = request.registry.settings

    schema = request.registry.getUtility(IRegisterSchema)
    schema = schema().bind(request=request)

    form_class = request.registry.getUtility(IRegisterForm)
    form = form_class(schema)

    social_logins = aslist(settings.get("websauna.social_logins", ""))

    if request.method == "POST":

        # If the request is a POST:
        controls = request.POST.items()
        try:
            captured = form.validate(controls)
        except deform.ValidationFailure as e:
            return {'form': e.render(), 'errors': e.error.children, 'social_logins': social_logins}

        # With the form validated, we know email and username are unique.
        del captured['csrf_token']

        registration_service = get_registration_service(request)
        return registration_service.sign_up(user_data=captured)

    return {'form': form.render(), 'social_logins': social_logins}


@view_config(route_name='activate')
def activate(request):
    """View to activate user after clicking email link."""
    code = request.matchdict.get('code', None)
    registration_service = get_registration_service(request)
    return registration_service.activate_by_email(code)


@view_config(route_name='login', renderer='login/login.html')
def login(request):
    """Default login view implementation."""

    login_redirect_view = get_config_route(request, "websauna.login_redirect")

    # Create login form schema
    schema = request.registry.getUtility(ILoginSchema)
    schema = schema().bind(request=request)

    # Create login form
    form = request.registry.getUtility(ILoginForm)
    form = form(schema)
    settings = request.registry.settings

    social_logins = aslist(settings.get("websauna.social_logins", ""))

    # Process form
    if request.method == "POST":

        try:
            controls = request.POST.items()
            captured = form.validate(controls)
        except deform.ValidationFailure as e:
            return {
                'form': e.render(),
                'errors': e.error.children
            }

        username = captured['username']
        password = captured['password']
        login_service = get_login_service(request)

        try:
            return login_service.authenticate_credentials(username, password, login_source="login_form")
        except AuthenticationFailure as e:

            # Tell user they cannot login at the moment
            messages.add(request, msg=str(e), msg_id="msg-authentication-failure", kind="error")

            return {
                'form': form.render(appstruct=captured),
                'errors': [e],
                "social_logins": social_logins
            }
    else:
        # HTTP get, display login form
        if request.user:
            # Already logged in
            return HTTPFound(location=login_redirect_view)

        # Display login form
        return {'form': form.render(), "social_logins": social_logins}


@view_config(route_name='registration_complete', renderer='login/registration_complete.html')
def registration_complete(request):
    """After activation initial login screen."""

    # Create login form schema
    schema = request.registry.getUtility(ILoginSchema)
    schema = schema().bind(request=request)

    # Create login form
    form = request.registry.getUtility(ILoginForm)
    form = form(schema)
    settings = request.registry.settings

    # Make sure we POST to right endpoint
    form.action = request.route_url('login')

    return {"form": form.render()}


@view_config(route_name='login_social')
def login_social(request):
    """Login using OAuth and any of the social providers."""

    # Get the internal provider name URL variable.
    provider_name = request.matchdict.get('provider_name')
    oauth_login_service = get_oauth_login_service(request)
    assert oauth_login_service, "OAuth not configured for {}".format(provider_name)
    return oauth_login_service.handle_request(provider_name)


@view_config(permission='authenticated', route_name='logout')
def logout(request):
    if request.method != "POST":
        # No GET / CSRF logouts
        return HTTPMethodNotAllowed()
    login_service = get_login_service(request)
    return login_service.logout()


@view_config(route_name='forgot_password', renderer='login/forgot_password.html')
def forgot_password(request):

    schema = request.registry.getUtility(IForgotPasswordSchema)
    schema = schema().bind(request=request)

    form = request.registry.getUtility(IForgotPasswordForm)
    form = form(schema)

    if request.method == 'POST':

        # From here on, we know it's a POST. Let's validate the form
        controls = request.POST.items()
        try:
            captured = form.validate(controls)
        except deform.ValidationFailure as e:
            # This catches if the email does not exist, too.
            return {'form': e.render(), 'errors': e.error.children}

        credential_activity_service = get_credential_activity_service(request)
        # Process valid form
        email = captured["email"]

        try:
            return credential_activity_service.create_forgot_password_request(email)
        except CannotResetPasswordException as e:
            messages.add(request, msg=str(e), msg_id="msg-cannot-reset-password", kind="error")
            return {'form': form.render()}

    return {'form': form.render()}


@view_config(route_name='reset_password', renderer='login/reset_password.html')
def reset_password(request):
    """Perform the actual reset based on the email reset link.

    User arrives on the page and enters the new password.
    """

    schema = request.registry.getUtility(IResetPasswordSchema)
    schema = schema().bind(request=request)

    form = request.registry.getUtility(IResetPasswordForm)
    form = form(schema)

    code = request.matchdict.get('code', None)
    credential_activity_service = get_credential_activity_service(request)
    user = credential_activity_service.get_user_for_password_reset_token(code)
    if not user:
        raise HTTPNotFound("Invalid password reset code")

    if request.method == 'POST':
        try:
            controls = request.POST.items()
            captured = form.validate(controls)
        except deform.ValidationFailure as e:
            return {'form': e.render(), 'errors': e.error.children}

        password = captured['password']

        return credential_activity_service.reset_password(code, password)

    # Question screen
    return {
        'form': form.render(
            appstruct=dict(
                user=user.friendly_name
            )
        )
    }