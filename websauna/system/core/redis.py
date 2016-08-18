"""Redis connection manager."""
import logging

from redis import StrictRedis
from redis import ConnectionError

from pyramid.config import Configurator
from pyramid.registry import Registry
from pyramid.threadlocal import get_current_registry

from websauna.system.http import Request
from websauna.compat.typing import Union


logger = logging.getLogger(__name__)


def get_redis(request_or_registry: Union[Request, Registry], url: str=None, redis_client=StrictRedis, **redis_options) -> StrictRedis:
    """Get a connection to Redis.

    Example:

    .. code-block:: python

        from websauna.system.core.redis import get_redis

        def my_view(request):
            redis = get_redis(request)
            redis.set("myval", "foobar")
            print(redis.get("myval))

    See :ref:`transient` data documentation.

    `See Redis command documentation <http://redis.io/commands>`_.

    `See Redis Python client <https://pypi.python.org/pypi/redis>`_.

    Compatible with *pyramid_redis_session*, see https://github.com/ericrasmussen/pyramid_redis_sessions/blob/master/pyramid_redis_sessions/connection.py

    TODO: Currently this method does not cache/pool connections.

    :param request: HTTP request object. NOTE: By legacy this argument also supports Registry object. However this behaviro will be deprecated.

    :param url: An optional connection string that will be passed straight to `StrictRedis.from_url`. The connection string should be in the form redis://username:password@localhost:6379/0. If not given use the default from settings.

    :param redis_options: A dict of keyword args to be passed straight to `StrictRedis`

    :return: Redis client
    """

    if isinstance(request_or_registry, Registry):
        # Unit test calling convention
        registry = request_or_registry
    else:
        registry = request_or_registry.registry

    if registry is None:
        # Should not happen any longer
        raise RuntimeError("Always pass registry explicitly to get_redis()")

    # TODO: Cache connections by name
    # attempt to get an existing connection from the registry
    redis = None

    # if we found an active connection, return it
    if redis is not None:
        return redis

    # if no url passed, try to get it from pyramid settings
    url = registry.settings.get('redis.sessions.url') if url is None else url
    # otherwise create a new connection
    if url is not None:
        # remove defaults to avoid duplicating settings in the `url`
        redis_options.pop('password', None)
        redis_options.pop('host', None)
        redis_options.pop('port', None)
        redis_options.pop('db', None)
        # the StrictRedis.from_url option no longer takes a socket
        # argument. instead, sockets should be encoded in the URL if
        # used. example:
        #     unix://[:password]@/path/to/socket.sock?db=0
        redis_options.pop('unix_socket_path', None)
        # connection pools are also no longer a valid option for
        # loading via URL
        redis_options.pop('connection_pool', None)
        redis = redis_client.from_url(url, **redis_options)
    else:
        raise RuntimeError("Redis connection options missing. Please configure redis.sessions.url")

    # TODO: Fix caching by redis options
    # save the new connection in the registry
    # setattr(registry, '_redis_sessions', redis)

    return redis


def is_sane_redis(config:Configurator) -> bool:
    """Check that we have a working Redis connection for session.

    Execute this on startup, so we bail out without starting up with a missing Redis.

    :return: True if Redis connection works
    """

    try:
        redis = get_redis(config.registry)
        redis.set("websauna_session_test", True)
        return True
    except ConnectionError as e:
        return False