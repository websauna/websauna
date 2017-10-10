.. _transient:

.. _redis:

==============
Transient data
==============

.. contents:: :local:

Introduction
============

In the context of Websauna transient data primarly means

* Visitor session data (authentication, shopping carts, etc.)

* Cache

* Other non-critical, fast and frequently accessed data

Websauna defaults to :term:`Redis` key value store for transient data storage.

Differences between persistent data (SQL) and transient data (Redis)
====================================================================

Transient data properties are along the lines of

* Which might not be around forever - does not satisfy ACID guarantees

* Might be cache-like data

* Might be user session data

* Is optimized for speed instead of persistence

* Might not be tied to normal database transaction lifecycle

* Might not have complex query properties like SQL, but is more key-value like

Using session data
==================

Session data is available for both logged in and anonymous users. Examples:

.. code-block:: python

    request.session["my_key"] = "value"  # Set a session value

    print(request.session["my_key"])  # Get a session value

    print(request.session.get("my_key")  # Get a session value, defaults to None if not yet set

See also :ref:`flash messages <messages>` and :py:meth:`websauna.system.Initializer.configure_sessions`.

For more information see `Sessions in Pyramid <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html>`_.

Getting Redis client
====================

Getting a hold a Redis client can be done with :py:func:`websauna.system.core.redis.get_redis` call.

Storing data
============

Redis stores all data, including numbers, internally as byte strings. For unicode strings (default Python strings), you must encode values yourself:

.. code-block:: python

    from websauna.system.core.redis import get_redis

    def my_view(request):
        redis = get_redis(request)
        redis.set("foo", "ÅÄÖ".encode("utf-8"))
        assert redis.get("foo").decode("utf-8") == "ÅÄÖ"

For more advanced example, see `SMS login <https://gist.github.com/miohtama/69b5c365ec5e5ddd1d0b2ad2869460e8>`_.

Exploring Redis database
========================

If you want to explore Redis database you can use

* ``redis-cli`` command line tool

* On site (:doc:`notebook <../misc/notebook>`

* :ref:`ws-shell` command line shell

Clearing Redis data in tests
============================

By default tests do not clear Redis database between tests run.

You can manually clear Redis at the beginning of your test code:

.. code-block:: python

    from websauna.system.core.redis import get_redis

    def test_brand_data(dbsession, test_request):
        """Verify brand data."""

        # Clear redis data for proper cache testing,
        # make sure we don't have existing data from previous test runs
        redis = get_redis(test_request)
        redis.flushdb()

Default Redis database numbering
================================

Redis database *1* is configured for local development/staging/production session and cache data.

Redis database *3* is configured for local development/staging/production Celery jobs.

Redis database *14* is configured for unit test session data.

Redis database *15* is configured for unit test Celery jobs.

Redis settings can be found in :ref:`base.ini` and `test.ini`.

Also see :ref:`Celery config <celery-config>` for more information.

Increasing session timeout
==========================

To make user sessions persistent, as in no need to relogin, you can set session timeout to a long value.

Add to your :ref:`production.ini`:

.. code-block:: ini

    #
    # Session
    #

    # Set cookie time out to one year
    redis.sessions.cookie_max_age = 31536000

    # Set redis session key timeout to one year
    redis.sessions.timeout = 31536000

    # No JavaScript access to cookies
    redis.sessions.cookie_secure = True
    # Only server session cookie over HTTPS
    redis.sessions.cookie_httponly = True

Backup
======

The default :doc:`backup <../ops/backup>` script backs up Redis database by dumping it.

More information
================

`See Redis command documentation <http://redis.io/commands>`_.

`See Redis Python client <https://pypi.python.org/pypi/redis>`_.

