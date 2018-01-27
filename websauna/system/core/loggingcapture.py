"""Extra logging context."""
# Standard Library
import logging

# Pyramid
from pyramid.request import Request

# SQLAlchemy
import sqlalchemy


logger = logging.getLogger(__name__)


def is_good_sqlalchemy_object(obj):
    """Let's not cause exceptions in exception handler/logger."""
    state = sqlalchemy.inspect(obj)
    return not state.detached


def get_logging_user_context(request: Request) -> dict:
    """Capture some extra user-specific information from the logging context.

    :return: Dict containing human readable user parameters to help identify the user on this request
    """
    try:
        user = getattr(request, "user", None)
    except sqlalchemy.exc.InvalidRequestError:
        # We had a rollback and could not capture the user,
        # because user has been rolled back
        user = None

    user_context = {}
    try:
        if user:
            if is_good_sqlalchemy_object(user):
                # Add additional user context to the logged exception
                username = getattr(user, "friendly_name", None) or getattr(user, "username", None) or str(user)
                email = getattr(user, "email", None)
                user_context.update(dict(user=username, email=email))
            else:
                user_context.update(dict(detached=True))

        # All the session data as JSON
        session = getattr(request, "session", None)
        if session:
            session = dict(session.items())
            user_context.update(dict(session=session))
        else:
            user_context.update(dict(session="No session data available in internal_server_error()"))

        user_context["ip"] = request.client_addr

        # TODO: Make this more generic
        # https://support.cloudflare.com/hc/en-us/articles/200168236-What-does-CloudFlare-IP-Geolocation-do-
        user_context["cloudflare_country"] = request.headers.get("cf-ipcountry")

        return user_context
    except Exception as e:
        logger.exception(e)
        logger.error("Failed to capture user context %s", request)
        return {}
