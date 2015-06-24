"""Rolling time window counter and rate limit using Redis.

Use Redis sorted sets to do a rolling time window counters and limiters.

More info

* http://redis.io/commands/zadd

"""

import time
from websauna.system.core.redis import get_redis


def _check(redis, key, window=60, limit=50):

    # Expire old keys (hits)
    expires = time.time() - window
    redis.zremrangebyscore(key, '-inf', expires)

    # Add a hit on the very moment
    now = time.time()
    redis.zadd(key, now, now)

    # If we currently have more keys than limit,
    # then limit the action
    if redis.zcard(key) > limit:
        return True

    return False


def _get(redis, key):
    """ Get the current hits per rolling time window.

    :param redis: Redis client

    :param key: Redis key name we use to keep counter

    :return: int, how many hits we have within the current rolling time window
    """
    return redis.zcard(key)


def check(registry, key, window=60, limit=10):
    """Do a rolling time window counter hit.

    Use ``key`` to store the current hit rate in Redis.

    :param registry: Pyramid registry e.g. request.registry
    :param key: Redis key name we use to keep counter
    :param window: Rolling time window in seconds. Default 60 seconds.
    :param limit: Allowed operations per time window. Default 10 hits.

    :return: True is the maximum limit has been reached for the current time window
    """
    redis = get_redis(registry)
    return _check(redis, key, window, limit)


def get(registry, key):
    """Get the current hits per rolling time window.

     Use ``key`` to store the current hit rate in Redis.

    :param registry: Pyramid registry e.g. request.registry
    :param key: Redis key name we use to keep counter
    :return: int, how many hits we have within the current rolling time window
    """
    redis = get_redis(registry)
    return _check(redis, key)
