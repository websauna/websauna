"""Default implementation of social login handling."""
# Standard Library
import logging

# Pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.settings import aslist
from zope.interface import implementer

from authomatic.adapters import WebObAdapter
from authomatic.core import LoginResult

# Websauna
from websauna.system.core import messages
from websauna.system.user.interfaces import AuthenticationFailure
from websauna.system.user.interfaces import IOAuthLoginService
from websauna.system.user.social import NotSatisfiedWithData
from websauna.system.user.utils import get_authomatic
from websauna.system.user.utils import get_login_service
from websauna.system.user.utils import get_social_login_mapper


logger = logging.getLogger(__name__)


@implementer(IOAuthLoginService)
class DefaultOAuthLoginService:

    def __init__(self, request: Request):
        self.request = request

    def handle_request(self, provider_name) -> Response:
        """Handle all requests coming to login/facebook, login/twitter etc. endpoints.

        * Login form does an empty HTTP POST request to initiate OAuth process

        * Federated authentication service does HTTP GET redirect when they accept OAuth authentication request
        """
        ae = AuthomaticLoginHandler(self.request, provider_name)
        response = ae.handle()
        return response


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

    def __init__(self, request: Request, provider_name: str):
        """Initialize AuthomaticLoginHandler.

        :param request: Pyramid request.
        :param provider_name: Authomatic provider name.
        """
        self.request = request
        self.provider_name = provider_name

        settings = request.registry.settings
        self.social_logins = aslist(settings.get("websauna.social_logins", ""))

        # Allow only logins which we configured
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

    def do_success(self, authomatic_result: LoginResult) -> Response:
        """Handle we got a valid OAuth login data.

        Try and log in the user.
        """
        user = self.mapper.capture_social_media_user(self.request, authomatic_result)
        try:
            login_service = get_login_service(self.request)
            return login_service.authenticate_user(user, login_source=self.provider_name)
        except AuthenticationFailure as e:
            messages.add(self.request, kind="error", msg=str(e), msg_id="msg-cannot-login-social-media-user")
            login_url = self.request.route_url("login")
            return HTTPFound(location=login_url)

    def do_error(self, authomatic_result: LoginResult, e: Exception) -> Response:
        """Handle getting error from OAuth provider."""
        # We got some error result, now let see how it goes
        if e:
            # Leave a cue for sysadmins everything is not right. Use INFO level as usually this is just the user pressing Cancel on the OAuth pop up screen.
            logger.info(e)

        messages.add(self.request, kind="error", msg=str(e), msg_id="msg-authomatic-login-error")
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
            """Having CSRF token in form data messes Authomatic internally so we strip it away with this hack.."""
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
