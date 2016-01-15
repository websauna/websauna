==============
Transient data
==============

.. contents:: :local:

Introduction
============

In the context of Websauna transient data primarly means

* Visitor session data (authentication, shopping carts, etc.)

* Cache

Furthermore transient data properties are along the lines of

* Which might not be around forever - does not satisfy ACID guarantees

* Might be cache-like data

* Might be user session data

* Is optimized for speed instead of persistence

* Might not be tied to normal database transaction lifecycle

* Might not have complex query properties like SQL, but is more key-value like

The stack component for managing transient data in Websauna is Redis.

Using session data
==================

Session data is available for both logged in and anonymous users. Examples::

    request.session["my_key"] = "value"  # Set a session value

    print(request.session["my_key"])  # Get a session value

    print(request.session.get("my_key")  # Get a session value, defaults to None if not yet set

See also :doc:`flash messages <../misc/messages>`_ and :py:meth:`websauna.system.Initializer.configure_sessions`.

For more information see `Sessions in Pyramid <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html>`_.

Default Redis behavior
======================

By default, Websauna uses :term:`Redis` for transient data storage.

Redis database mappings
-----------------------

Redis database *1* is configured for local development/staging/production session and cache data.

Redis database *3* is configured for local development/staging/production Celery jobs.

Redis database *14* is configured for unit test session data.

Redis database *15* is configured for unit test Celery jobs.

See :ref:`Celery config <celery-config>` for more information.

Configuration
=============

Redis settings can be found in :ref:`base.ini` and `test.ini`.

Accessing Redis
===============

Getting a hold a Redis client can be done with :py:func:`websauna.system.core.get_redis` call.

Exploring Redis database
========================

If you want to explore Redis database you can use ``redis-cli`` command line tool or Python shell (:ref:`notebook` :ref:`ws-shell`) to explore the contents of Redis database

Backup
======

The default :doc:`backup <../ops/backup>` script backs up Redis database by dumping it.


