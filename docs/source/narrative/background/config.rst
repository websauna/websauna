=============
Configuration
=============

Websauna uses `INI-based configuration files <https://en.wikipedia.org/wiki/INI_file>`_, stemming from Paste and Pyramid legacy. Each command line command or WSGI web application launch module takes one of these INI files as an input. INI file tells

Configuration structure
=======================

Websauna INI configuration files are extensible. You can include base INI configuration files in your settings file from file system and other Python packages.

Websauna package defines three configuration files which you should use

Configuration inclusion
=======================

.. note ::

    Configuraiton inclusion system will be phased out in the future versions to be replaced with more generic configuration solution.

Configuration variables
=======================

The following variables are available

websauna.site_url
-----------------

Where this site is running. When serving web pages, this value is not accessed, as ``request.route_url()`` and similar methods rely on the HTTP headers coming from the web server.

The value is mostly used when running tasks and command line scripts.

Default: No default, must be set.

websauna.cachebust
------------------

Use Pyramid cache busting mechanism when serving static assets.

This option controls whether or not static assets are served in production deployment or CDN mode.

Enable this in production deployments to have never expiring URLs for all items referred by ``request.static_url()`` or ``{{ 'xxx'|static_url }}`` in templates.

URLs are tagged by file MD5 hash. If the source asset file (CSS, JS image) changes a new URL is generated, invalidating the cache.

Default:: ``False``.

More info

* http://docs.pylonsproject.org/projects/pyramid/en/1.6-branch/narr/assets.html#cache-busting-and-asset-overrides

websauna.cache_max_age
----------------------

How long *Expires* header is set for served static assets.

Default: ``None`` (zero) seconds. In production configuration this is overridden to 3600 seconds.

websauna.superuser
------------------

List of superuser emails or usernames. Add your username on this list to make it super user.

Example::

    websauna.superuser =
        admin
        mikko@example.com

.. warning::

    Superuser permission allows executing arbitrary code on the server.

More information

* See :doc:`Notebook documentation <./notebook>`

websauna.global_config
----------------------

This is a reference to ``global_config`` object which is used to initialize Pyramid application. It is a dictionary. Example::

    {'__file__': '/Users/mikko/code/trees/trees/development.ini', 'here': '/Users/mikko/code/trees/trees'}


websauna.sanity_check
---------------------

Perform database sanity check after the startup. This will check all models have corresponding tables and columns in the database and there are no unsynced models.

Disabled for testing.

Default: ``true``

websauna.social_logins
----------------------

List of configured social logins, or federated authentication, methods.

* List can be space or new line separated

* Each social login corresponds one entry in secrets INI file

Example value::

    websauna.social_logins =
        facebook
        twitter

In which case your secrets INI would contain::

       [facebook]
        class = authomatic.providers.oauth2.Facebook
        consumer_key = xxx
        consumer_secret = yyy
        scope = user_about_me, email
        mapper = websauna.system.user.social.FacebookMapper

        [twitter]
        class = authomatic.providers.oauth1.Twitter
        consumer_key = xxx
        consumer_secret = yyy
        ...


websauna.force_utc_on_columns
-----------------------------

Enforce that all datetime values going to SQLAlchemy models are timezone-aware and in UTC timezone.

It is a recommended best practice that you store only UTC dates and times in SQL databases. SQL databases themselves are very naive what comes to storing timezones are doing time operations in SQL. Storing everything in UTC and doing timezones on the application side is one way to ensure consistency.

* When you set a value on datetime is must contain timezone information, naive datetime objects are not accepted

* Time is converted to UTC

* Datetime is stored in the database

If set to to true the application will fail with assertion error if you try to store non-UTC datetime.

Default: ``true``

For more information see :py:mod:`websauna.system.model.sqlalchemyutcdatetime`.


websauna.allowed_hosts
----------------------

Whitespace separated list of hostnames this site is allowed to respond.

This is a security feature preventing direct IP access of sites.

Set this to list of your production domain names::

    websauna.allowed_hosts =
        libertymusicstore.net
        upload.libertymusicstore.net

Default: ``localhost``.


websauna.error_test_trigger
---------------------------

If set enable a view at path ``/error-trigger`` that generates a runtime error.

You can use this view to generate an error and see that your logging and error monitoring system functions correctly.

Default: ``False``.

websauna.test_web_server_port
-----------------------------

A port where to run the test server for functional tests.

This is used by ``web_server`` py.test test fixture.

Default: ``8521``.

Configuration variables from other packages
===========================================

* Paste

* Alembic

* pyramid_redis

* sqlalchemy

* Python logging

* `pyramid_notebook <https://bitbucket.org/miohtama/pyramid_notebook>`_