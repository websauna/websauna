"""Session creation."""
import logging

from pyramid_redis_sessions import session_factory_from_settings
from websauna.utils.time import now


logger = logging.getLogger(__name__)


def set_creation_time_aware_session_factory(config):
    """Setup a session factory that rememembers time when the session was created.

    We need this information to later invalidate session for the authentication change details.
    """

    settings = config.registry.settings

    # special rule for converting dotted python paths to callables
    for option in ('client_callable', 'serialize', 'deserialize',
                   'id_generator'):
        key = 'redis.sessions.%s' % option
        if key in settings:
            settings[key] = config.maybe_dotted(settings[key])

    session_factory = session_factory_from_settings(settings)

    def create_session(request):
        session = session_factory(request)
        if "created_at" not in session:
            session["created_at"] = now()
            session["client_addr"] = request.client_addr

        # TODO:
        # For some Redis session backends, looks like we may have a race condition creatin CSRF token (no idea how?),
        # and thus we call get_csrf_token() here to explicitly trace and check it
        ensure_csrf = session.get_csrf_token()
        logger.debug("Created session %s %s %s", request.client_addr, session.session_id, ensure_csrf)
        return session

    config.set_session_factory(create_session)
