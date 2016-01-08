=============
Configuration
=============

Websauna uses `INI-based configuration files <https://en.wikipedia.org/wiki/INI_file>`_, from Paste and Pyramid legacy. To avoid copy-pasted configuration settings

Configuration structure
=======================

Websauna INI configuration files are extensible. You can include base INI configuration files in your settings file from file system and other Python packages.

The default app scaffold drops five files specific to your app

* ``base.ini``

* ``development.ini``

* ``test.ini``

* ``staging.ini``

* ``production.ini``

All these files extend Websauna base configuration files using the configuration inclusion mechhanism explained below.

All files can have corresponding :term:`secrets` INI file which does not go to the version control and must be hand placed around.

.. _base.ini:

base.ini
--------

This is the base for all configuration files. It should not be used standalone, but it is base for all settings.

* Set up loggers

* Set up core settings like Jinja 2 templating

* Set up default websauna configuration variables

See :download:`base.ini <../../../development.ini>`.

development.ini
---------------

This a the configuration file for running the local development server

* No outgoing email

* Celery jobs are executed eagerly, no need to run Celery process

* No backups

* Development databases

* Enable all Pyramid debug options.

* Enable :term:`pyramid_debugtoolbar`.

See :download:`development.ini <../../../development.ini>`.

test.ini
--------

Settings for running unit tests

* No outgoing email

* Test database

* Jinja templates in strict mode (raise exception on missing template variable)

See :download:`development.ini <../../../test.ini>`.

production.ini
--------------

Settings for runnign Websauna on production server.

* Mail out

* Production database

* No debugging

* Cached static files

See :download:`production.ini <../../../production.ini>`.

staging.ini
-----------

Same as `production.ini`, but with staging secrets, so that you can use different API credentials for a staging server and production server.

See :download:`staging.ini <../../../staging.ini>`.

secrets
-------

All INI files have a corresponding secrets pair (``development-secrets.ini``, ``production-secrets.ini``). Websauna app :term:`scaffold` places these files to :term:`.gitignore`, so that you cannot accidentally put potentially confidential information to a version control.

Configuration inclusion
=======================

For examples see any INI file produced by :term:`scaffold`.

.. note ::

    Configuraition inclusion system will be phased out in the future versions to be replaced with more generic configuration solution.

Websauna configuration variables
================================

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

.. _celery-config:

Configuration from other packages

Celery
------

Websauna uses :term:`pyramid_celery` which allows you to put :term:`Celery` configuration variables to a INI file.

For example see Websauna base.ini. `For more information see Celert configuration <http://docs.celeryproject.org/en/latest/configuration.html>`_.

Alembic
-------

`See Alembic <http://alembic.readthedocs.org/en/latest/tutorial.html#editing-the-ini-file>`_.

pyramid_redis
-------------

`See pyramid_redis <http://pyramid-redis-sessions.readthedocs.org/en/latest/gettingstarted.html>`_.

sqlalchemy
----------

.. _sqlalchemy.url:

sqlalchemy.url
++++++++++++++

The connection string for the primary SQL database.

Follows `SQLAlchemy engine configuration syntax <http://docs.sqlalchemy.org/en/latest/core/engines.html>`_.

Default: ``postgresql://localhost/yourappname_dev`` (for :term:`development.ini`)

Python logging
--------------

`See Python guide <http://docs.python-guide.org/en/latest/writing/logging/#example-configuration-via-an-ini-file>`_.

pyramid_notebook
----------------

`See pyramid_notebook <https://bitbucket.org/miohtama/pyramid_notebook>`_.