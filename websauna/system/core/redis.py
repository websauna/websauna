"""Redis connection manager."""
import logging

from redis import StrictRedis
from redis import ConnectionError

from pyramid.config import Configurator
from pyramid.registry import Registry
from pyramid.threadlocal import get_current_registry


logger = logging.getLogger(__name__)


def get_redis(registry:Registry=None, url:str=None, redis_client=StrictRedis, **redis_options):
    """Get a connection to Redis.

    Compatible with *pyramid_redis_session*, see https://github.com/ericrasmussen/pyramid_redis_sessions/blob/master/pyramid_redis_sessions/connection.py

    Default Redis connection handler. Once a connection is established it is
    cached in ``registry``.

    Shell example::

        from websauna.system.core.redis import get_redis
        redis = get_redis(registry)

        print(redis.keys())

    Parameters:

    ``registry`` Pyramid registry


    ``url``
    An optional connection string that will be passed straight to
    `StrictRedis.from_url`. The connection string should be in the form:
        redis://username:password@localhost:6379/0

    ``settings``
    A dict of keyword args to be passed straight to `StrictRedis`

    Returns:

    An instance of `StrictRedis`
    """

    if registry is None:
        logger.warn("Always pass registry explicitly to get_redis()")
        registry = get_current_registry()

    # TODO: Cache connections by name
    # attempt to get an existing connection from the registry
    redis = None

    # if we found an active connection, return it
    if redis is not None:
        return redis

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
        redis = redis_client(**redis_options)

    # TODO: Fix caching by redis options
    # save the new connection in the registry
    # setattr(registry, '_redis_sessions', redis)

    return redis


def is_sane_redis(config:Configurator) -> bool:
    """Check that we have a working Redis connection for session."""

    try:
        redis = get_redis(config.registry)
        redis.set("websauna_session_test", True)
        return True
    except ConnectionError as e:
        return False