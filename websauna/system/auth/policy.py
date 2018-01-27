# Pyramid
from pyramid.authentication import \
    SessionAuthenticationPolicy as _SessionAuthenticationPolicy

# Websauna
from websauna.utils.time import now


class SessionAuthenticationPolicy(_SessionAuthenticationPolicy):
    """Session authentication policy which makes sure all responses get vary: Cookie.

    Originally from https://github.com/pypa/warehouse/blob/master/warehouse/accounts/auth_policy.py
    """

    #: Session has this key set to the timestamp when the user authentication happened. The key is removed when the user logs out.
    authenticated_at_key = "authenticated_at"

    #: This is the timestamp when this session logged out last time
    unauthenticated_at_key = "unauthenticated_at"

    def remember(self, request, userid, **kw):
        """ Store a userid in the session."""
        request.session[self.userid_key] = userid

        # Do not lose the original log in timestamp if we get multiple calls to remember()
        if self.authenticated_at_key not in request.session:
            request.session[self.authenticated_at_key] = now()

        return []

    def forget(self, request):
        """User logs out or is forced to be forgotten."""

        # Wiggle session keys so that we know when unauthentication happened
        request.session[self.unauthenticated_at_key] = now()

        # Remove authenticated_at timestamp so nothing can read it when there is no logged in associated user
        if self.authenticated_at_key in request.session:
            del request.session[self.authenticated_at_key]

        return super().forget(request)

    def unauthenticated_userid(self, request):
        """What is the user id for unauthenticated users."""

        # If we're calling into this API on a request, then we want to register
        # a callback which will ensure that the response varies based on the
        # Cookie header.
        # request.add_response_callback(add_vary_callback_if_cookie("Cookie"))

        # Dispatch to the real SessionAuthenticationPolicy
        return super().unauthenticated_userid(request)
