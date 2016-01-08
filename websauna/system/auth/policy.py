from pyramid.authentication import SessionAuthenticationPolicy as _SessionAuthenticationPolicy

from websauna.system.http.header import add_vary_callback
from websauna.utils.time import now


class SessionAuthenticationPolicy(_SessionAuthenticationPolicy):
    """Session authentication policy which makes sure all responses get vary: Cookie.

    Originally from https://github.com/pypa/warehouse/blob/master/warehouse/accounts/auth_policy.py
    """

    created_at_key = "created_at"

    def remember(self, request, userid, **kw):
        """ Store a userid in the session."""
        request.session[self.userid_key] = userid
        request.session[self.created_at_key] = now()
        return []

    def unauthenticated_userid(self, request):
        # If we're calling into this API on a request, then we want to register
        # a callback which will ensure that the response varies based on the
        # Cookie header.
        request.add_response_callback(add_vary_callback("Cookie"))

        # Dispatch to the real SessionAuthenticationPolicy
        return super().unauthenticated_userid(request)
