"""Session management."""

import logging
import pickle as cPickle
import functools

from pyramid_redis_sessions import get_default_connection
from pyramid_redis_sessions.util import persist, _parse_settings, get_unique_session_id
from pyramid_redis_sessions import _set_cookie
from pyramid_redis_sessions import _generate_session_id
from pyramid_redis_sessions import RedisSession
from pyramid_redis_sessions import _delete_cookie, _cookie_callback, _get_session_id_from_cookie

from websauna.utils.time import now


logger = logging.getLogger(__name__)


class WebsaunaSession(RedisSession):
    """A specialized session handler that supports initial parameters.

    We can pass `initial_data` that prepopulates session data keys when the session is written for the first time. Usually this is when CSRF token is genratd.

    .. note ::

        Move this to upstream pyramid_redis_session - its development has stalled for now
    """

    def __init__(
        self,
        initial_data: dict,
        redis,
        session_id,
        new,
        new_session,
        serialize=cPickle.dumps,
        deserialize=cPickle.loads,
        ):
        super().__init__(redis, session_id, new, new_session, serialize, deserialize)
        self.initial_data = initial_data

    @persist
    def __setitem__(self, key, value):

        # Check if do not have any values in the session and then initialize its data
        if self.managed_dict:
            self.managed_dict.update(self.initial_data)
        self.managed_dict[key] = value


def WebsaunaSessionFactory(
    secret,
    timeout=1200,
    cookie_name='session',
    cookie_max_age=None,
    cookie_path='/',
    cookie_domain=None,
    cookie_secure=False,
    cookie_httponly=True,
    cookie_on_exception=True,
    url=None,
    host='localhost',
    port=6379,
    db=0,
    password=None,
    socket_timeout=None,
    connection_pool=None,
    encoding='utf-8',
    encoding_errors='strict',
    unix_socket_path=None,
    client_callable=None,
    serialize=cPickle.dumps,
    deserialize=cPickle.loads,
    id_generator=_generate_session_id,
    cookieless_headers=["expires", "cache-control"],
    klass=WebsaunaSession,
    ):
    """
    Overrides the RedisSessionFactory with Websauna specifi functionality.

    .. note ::

        Due to functional paradigm, there was no clean way to override this.
        Move this to upstream pyramid_redis_session - its development has stalled for now

    Constructs and returns a session factory that will provide session data
    from a Redis server. The returned factory can be supplied as the
    ``session_factory`` argument of a :class:`pyramid.config.Configurator`
    constructor, or used as the ``session_factory`` argument of the
    :meth:`pyramid.config.Configurator.set_session_factory` method.

    Parameters:

    ``secret``
    A string which is used to sign the cookie.

    ``timeout``
    A number of seconds of inactivity before a session times out.

    ``cookie_name``
    The name of the cookie used for sessioning. Default: ``session``.

    ``cookie_max_age``
    The maximum age of the cookie used for sessioning (in seconds).
    Default: ``None`` (browser scope).

    ``cookie_path``
    The path used for the session cookie. Default: ``/``.

    ``cookie_domain``
    The domain used for the session cookie. Default: ``None`` (no domain).

    ``cookie_secure``
    The 'secure' flag of the session cookie. Default: ``False``.

    ``cookie_httponly``
    The 'httpOnly' flag of the session cookie. Default: ``True``.

    ``cookie_on_exception``
    If ``True``, set a session cookie even if an exception occurs
    while rendering a view. Default: ``True``.

    ``url``
    A connection string for a Redis server, in the format:
    redis://username:password@localhost:6379/0
    Default: ``None``.

    ``host``
    A string representing the IP of your Redis server. Default: ``localhost``.

    ``port``
    An integer representing the port of your Redis server. Default: ``6379``.

    ``db``
    An integer to select a specific database on your Redis server.
    Default: ``0``

    ``password``
    A string password to connect to your Redis server/database if
    required. Default: ``None``.

    ``client_callable``
    A python callable that accepts a Pyramid `request` and Redis config options
    and returns a Redis client such as redis-py's `StrictRedis`.
    Default: ``None``.

    ``serialize``
    A function to serialize the session dict for storage in Redis.
    Default: ``cPickle.dumps``.

    ``deserialize``
    A function to deserialize the stored session data in Redis.
    Default: ``cPickle.loads``.

    ``id_generator``
    A function to create a unique ID to be used as the session key when a
    session is first created.
    Default: private function that uses sha1 with the time and random elements
    to create a 40 character unique ID.

    ``cookieless_headers``
    If view has set any of these response headers do not add a session
    cookie on this response. This way views generating cacheable content,
    like images, can signal the downstream web server that this content
    is safe. Otherwise if we set a cookie on these responses it could
    result to user session leakage.

    The following arguments are also passed straight to the ``StrictRedis``
    constructor and allow you to further configure the Redis client::

      socket_timeout
      connection_pool
      encoding
      encoding_errors
      unix_socket_path
    """
    def factory(request, initial_data, new_session_id=get_unique_session_id):
        redis_options = dict(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            connection_pool=connection_pool,
            encoding=encoding,
            encoding_errors=encoding_errors,
            unix_socket_path=unix_socket_path,
            )

        # an explicit client callable gets priority over the default
        redis = client_callable(request, **redis_options) \
            if client_callable is not None \
            else get_default_connection(request, url=url, **redis_options)

        # attempt to retrieve a session_id from the cookie
        session_id_from_cookie = _get_session_id_from_cookie(
            request=request,
            cookie_name=cookie_name,
            secret=secret,
            )

        new_session = functools.partial(
            new_session_id,
            redis=redis,
            timeout=timeout,
            serialize=serialize,
            generator=id_generator,
            )

        if session_id_from_cookie and redis.exists(session_id_from_cookie):
            session_id = session_id_from_cookie
            session_cookie_was_valid = True
        else:
            session_id = new_session()
            session_cookie_was_valid = False

        session = klass(
            initial_data,
            redis=redis,
            session_id=session_id,
            new=not session_cookie_was_valid,
            new_session=new_session,
            serialize=serialize,
            deserialize=deserialize,
            )

        set_cookie = functools.partial(
            _set_cookie,
            session,
            cookie_name=cookie_name,
            cookie_max_age=cookie_max_age,
            cookie_path=cookie_path,
            cookie_domain=cookie_domain,
            cookie_secure=cookie_secure,
            cookie_httponly=cookie_httponly,
            secret=secret,
            )
        delete_cookie = functools.partial(
            _delete_cookie,
            cookie_name=cookie_name,
            cookie_path=cookie_path,
            cookie_domain=cookie_domain,
            )
        cookie_callback = functools.partial(
            _cookie_callback,
            session,
            session_cookie_was_valid=session_cookie_was_valid,
            cookie_on_exception=cookie_on_exception,
            set_cookie=set_cookie,
            delete_cookie=delete_cookie,
            cookieless_headers=cookieless_headers,
            )
        request.add_response_callback(cookie_callback)

        return session

    return factory


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

    options = _parse_settings(settings)
    session_factory = WebsaunaSessionFactory(**options)

    def create_session(request):

        # Pass in the the data we use to track session on the server side.
        # Esp. created_at is used to later manually purge old sessions
        initial_data = {
            "client_addr": request.client_addr,
            "created_at": now(),
        }

        session = session_factory(request, initial_data)
        return session

    config.set_session_factory(create_session)
