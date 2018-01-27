"""Authentication tweens."""
# Standard Library
import logging

# Pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.registry import Registry

# SQLAlchemy
from sqlalchemy import orm

# Websauna
from websauna.system.core import messages
from websauna.system.http import Request


try:
    from pyramid_tm import reify  # noQA
    good_reify = True
except ImportError:
    good_reify = False


logger = logging.getLogger(__name__)


class SessionInvalidationTweenFactory:
    """Tween to detect invalidated sessions and redirect user back to home.

    This tween checks if the current session is logged in user and there has been authentication sensitive changes to this user. In this case all user sessions should be logged out.
    """

    def __init__(self, handler, registry: Registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request: Request):
        user = request.user
        if user:
            try:
                session_authenticated_at = request.session.get("authenticated_at")

                # User was deauthenticatd in this request for some reason
                if session_authenticated_at:

                    if not user.is_valid_session(session_authenticated_at):
                        request.session.invalidate()
                        messages.add(request, kind="error", msg="Your have been logged out due to authentication changes.", msg_id="msg-session-invalidated")
                        logger.info("User log out forced due to security sensitive settings change, user %s, session id %s", user, request.session.session_id)
                        return HTTPFound(request.application_url)
            except orm.exc.DetachedInstanceError:
                if good_reify:
                    # pyramid_tm 2.0
                    raise

                # TODO: pyramid_tm 2.0 needed,
                # now temporary just kill user object instead of failing with an internal error, so that development server doesn't fail with CSS etc. resources
                request.user = None

        response = self.handler(request)
        return response
