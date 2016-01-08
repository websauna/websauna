"""Session creation."""
from pyramid_redis_sessions import session_factory_from_settings
from websauna.utils.time import now


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
        return session

    config.set_session_factory(create_session)
