"""Core events."""

# Websauna
from websauna.system.http import Request


class InternalServerError:
    """Fired when internal server error page is rendered.

    Event can be consumed by monitoring addons like websauna.sentry.
    """

    def __init__(self, exception: Exception, request: Request):
        self.exception = exception
        self.request = request
