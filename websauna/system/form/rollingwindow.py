"""Rolling time window counter and rate limit using Redis.

Use Redis sorted sets to do a rolling time window counters and limiters. These are useful for preventing denial of service, flood and reputation attack against site elements which trigegr outgoing action (email, SMS).

Example how to do a Colander validator which checks that the form has not been submitted too many times within the time period::

    import colander as s

    @c.deferred
    def throttle_invites_validator(node, kw):
        "Protect invite functionality from flood attacks."
        request = kw["request"]

        limit = int(request.registry.settings.get("trees.invite_limit", 60))

        def inner(node, value):
            # Check we don't have many invites going out
            if rollingwindow.check(request.registry, "invite_friends", window=3600, limit=limit):

                # Alert devops through Sentry
                logger.warn("Excessive invite traffic")

                # Tell users slow down
                raise c.Invalid(node, 'Too many outgoing invites at the moment. Please try again later.')

        return inner

Then you construct form::

    schema = schemas.InviteFriends(validator=schemas.throttle_invites_validator).bind(request=request)
    form = deform.Form(schema)

You can also exercise this code in tests::

    def test_flood_invite(web_server, browser, dbsession, init):
        "Overload invites and see we get an error message."

        b = browser
        with transaction.manager:
            create_user()

        # Set flood limit to two attempts
        init.config.registry.settings["trees.invite_limit"] = "2"

        # Clear Redis counter for outgoing invitations
        redis = get_redis(init.config.registry)
        redis.delete("invite_friends")

        # Login
        b.visit(web_server + "/login")
        b.fill("username", EMAIL)
        b.fill("password", PASSWORD)
        b.find_by_name("Log_in").click()

        def flood():
            b.visit("{}/invite-friends".format(web_server))
            b.find_by_css("#nav-invite-friends").click()
            b.fill("phone_number", "555 123 1234")
            b.find_by_name("invite").click()

        flood()
        assert b.is_text_present("Invite SMS sent")
        flood()
        assert b.is_text_present("Invite SMS sent")
        flood()
        assert b.is_text_present("Too many outgoing invites at the moment")


More info

* http://opensourcehacker.com/2014/07/09/rolling-time-window-counters-with-redis-and-mitigating-botnet-driven-login-attacks/

* http://redis.io/commands/zadd

"""

# Standard Library
import time

# Websauna
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
