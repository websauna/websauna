"""Deform throttling support."""

import logging
import colander as c

from . import rollingwindow


logger = logging.getLogger(__name__)


def create_throttle_validator(name:str, max_actions_in_time_window:int, time_window_in_seconds:int=3600):
    """Creates a Colander form validator which prevents form submissions exceed certain rate.

    Form submissions are throttled system wide. This prevents abuse of the system by flooding it with requests.

    A logging warning is issued if the rate is exceeded. The user is greeted with an error message telling the submission is not possible at the moment.

    Example::

        from tomb_routes import simple_route

        from websauna.system.form.throttle import create_throttle_validator

        from myapp import schemas

        @simple_route("/login", route_name="login", renderer="login/login.html", append_slash=False)
        def login(request):

            # Read allowed email login rate from the config file
            email_login_rate = int(request.registry.settings.get("trees.email_login_rate", 50))

            # Create a Colander schema instance with rate limit validator
            email_schema = schemas.LoginWithEmail(validator=create_throttle_validator("email_login", email_login_rate)).bind(request=request)

    :param name: Identify this throttler. Used as a Redis key.

    :param max_actions_in_time_window: Number of allowed actions per window

    :param time_window_in_seconds: Time in window in seconds. Default one hour, 3600 seconds.

    :return: Function to be passed to ``validator`` Colander schema construction parameter.
    """

    @c.deferred
    def throttle_validator(node, kw):
        """Protect invite functionality from flood attacks."""
        request = kw["request"]

        limit = max_actions_in_time_window

        def inner(node, value):
            # Check we don't have many invites going out
            if rollingwindow.check(request.registry, "throttle_" + name, window=time_window_in_seconds, limit=limit):

                # Alert devops through Sentry
                logger.warn("Excessive form submissions on %s", name)

                # Tell users slow down
                raise c.Invalid(node, 'Too many form submissions at the moment. Please try again later.')

        return inner

    return throttle_validator
