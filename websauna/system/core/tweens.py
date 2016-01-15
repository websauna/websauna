"""Core tweens."""

from pyramid.registry import Registry
from pyramid.session import check_csrf_token
from websauna.system.http import Request


class EnforcedCSRFCheck:
    """Tween to always check CSRF token for HTTP POST requests."""

    def __init__(self, handler, registry:Registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request: Request):

        if request.method == "POST":

            # TODO: Add mechanism for views to whitelist POST with the token

            check_csrf_token(request)

        response = self.handler(request)
        return response