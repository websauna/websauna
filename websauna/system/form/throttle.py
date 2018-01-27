"""Deform throttling support."""
# Standard Library
import logging
import typing as t

# Pyramid
import colander as c
from pyramid import httpexceptions

# Websauna
from websauna.system.core.redis import get_redis
from websauna.system.http import Request

from . import rollingwindow


logger = logging.getLogger(__name__)


def create_throttle_validator(name: str, max_actions_in_time_window: int, time_window_in_seconds: int=3600):
    """Creates a Colander form validator which prevents form submissions exceed certain rate.

    The benefit of using validator instead of :func:`throttle_view` decorator is that we can give a nice
    Colander form error message instead of an error page.

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


def _read_throttle_settings(settings, setting):

    setting_value = settings.get(setting)
    if not setting_value:
        raise RuntimeError("Cannot read setting: {}".format(setting))

    parts = setting_value.split("/")
    if len(parts) != 2:
        raise RuntimeError("Bad throttle setting format: {}".format(setting_value))

    try:
        window = int(parts[0])
        limit = int(parts[1])
    except ValueError:
        raise RuntimeError("Could not parse: {}".format(setting_value))

    return limit, window


def throttled_view(
        rolling_window_id: t.Optional[str]=None,
        time_window_in_seconds: int=3600,
        limit: int=50,
        setting: t.Optional[str]=None):
    """Decorate a view to protect denial-of-service attacks using throttling.

    If the global throttling limit is exceeded the client gets HTTP 429 error.

    Internally we use :py:mod:`websauna.system.form.rollingwindow` hit counting implementation.

    Example that allows 30 page loads per hour:

    .. code-block:: python

        @view_config(
            name="new-phone-number",
            renderer="wallet/new_phone_number.html",
            decorator=throttled_view(limit=30, time_window_in_seconds=3600))
        def new_phone_number(request):
            # ... code goes here ...

    You can also configure the limit in a INI settings file.

    Example ``production.ini``:

    .. code-block:: ini

        magiclogin.email_throttle = 50/3600

    .. code-block:: python

        @view_config(
            name="email-login",
            renderer="wallet/new_phone_number.html",
            decorator=throttled_view(setting="magiclogin.email_throttle")
        def new_phone_number(request):
            # ... code goes here ...

    :param rolling_window_id: The Redis key name used to store throttle state. If not given a key derived from view name is used.

    :param time_window_in_seconds: Sliding time window for counting hits

    :param limit: Allowed number of hits in the given time window

    :param setting: Read throttle information from a INI settings. In this case string must be in format limit/time_window_seconds. Example: 50/3600. This overrides any given time and limit argument.

    :raise: :py:class:`pyramid.httpexceptions.HTTPTooManyRequests` if the endpoint gets hammered too much
    """
    # http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/views/chaining_decorators.html
    def outer(view_callable: t.Callable):

        name = view_callable.__name__

        if not rolling_window_id:
            key_name = "throttle_{key}".format(key=name)
        else:
            key_name = "throttle_{key}".format(key=rolling_window_id)

        def inner(context, request):

            if setting:
                hits, window = _read_throttle_settings(request.registry.settings, setting)
            else:
                window = time_window_in_seconds
                hits = limit

            if rollingwindow.check(request.registry, key_name, window=window, limit=hits):
                raise httpexceptions.HTTPTooManyRequests("Too many requests against {}".format(name))

            return view_callable(context, request)

        return inner

    return outer


def clear_throttle(request: Request, key_name: str):
    """Clear the throttling status.

    Example:

    .. code-block:: python

        clear_throttle(request, "new-phone-number")

    """
    redis = get_redis(request)
    redis.delete("throttle_{}".format(key_name))
