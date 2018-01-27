"""Redis connection manager."""
# Standard Library
import logging
import os
import threading
import typing as t

# Pyramid
from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.registry import Registry

from redis import ConnectionError
from redis import ConnectionPool
from redis import StrictRedis

# Websauna
from websauna.system.http import Request


logger = logging.getLogger(__name__)


def create_redis(registry: Registry, connection_url=None, redis_client=StrictRedis, max_connections=16, **redis_options) -> StrictRedis:
    """Sets up Redis connection pool once at the start of a process.

    Connection pool life cycle is the same as Pyramid registry which is the life cycle of a process (all threads).

    :param max_connections: Default per-process connection pool limit
    """

    # if no url passed, try to get it from pyramid settings
    url = registry.settings.get('redis.sessions.url') if connection_url is None else connection_url
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

        process_name = os.getpid()
        thread_name = threading.current_thread().name

        logger.info("Creating a new Redis connection pool. Process %s, thread %s, max_connections %d", process_name, thread_name, max_connections)

        connection_pool = ConnectionPool.from_url(url, max_connections=max_connections, **redis_options)
        redis = StrictRedis(connection_pool=connection_pool)
    else:
        raise RuntimeError("Redis connection options missing. Please configure redis.sessions.url")

    return redis


def log_redis_statistics(redis: StrictRedis):
    """Log Redis connection pool statistics at the end of each request.

    Help to diagnose connection problems and web process lifetime issues.

    We do not need to do specific cleanup, as connnection pool *should* clean up the connections when they go out of scope. Each Redis client function calls connection.release() at the end of operation."
    """
    pool = redis.connection_pool

    max_connections = pool.max_connections
    created = pool._created_connections
    available = len(pool._available_connections)
    in_use = len(pool._in_use_connections)

    process_name = os.getpid()
    thread_name = threading.current_thread().name

    logger.debug("Redis connection statistics - process: %s, thread: %s, created: %d, max: %d, in-use: %d, available: %d", process_name, thread_name, created, max_connections, available, in_use)


def get_redis(request_or_registry: t.Union[Request, Registry], url: str=None, redis_client=StrictRedis, **redis_options) -> StrictRedis:
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

    :param request: HTTP request object. NOTE: By legacy this argument also supports Registry object. However this behaviro will be deprecated.

    :param url: An optional connection string that will be passed straight to `StrictRedis.from_url`. The connection string should be in the form redis://username:password@localhost:6379/0. If not given use the default from settings.

    :param redis_options: A dict of keyword args to be passed straight to `StrictRedis`

    :return: Redis client
    """
    # TODO: Resolve calling convention only using one
    if isinstance(request_or_registry, Registry):
        # Unit test calling convention
        registry = request_or_registry
        # request = None
    else:
        registry = request_or_registry.registry
        # request = request_or_registry

    redis = registry.redis
    return redis


def is_sane_redis(config: Configurator) -> bool:
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


@subscriber(NewRequest)
def on_request_log_redis_stats(event):
    """On every request dump Redis diagnostics information."""
    redis = get_redis(event.request)
    log_redis_statistics(redis)
