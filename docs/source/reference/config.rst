.. _config:

=============
Configuration
=============

Websauna uses `INI-based configuration files <https://en.wikipedia.org/wiki/INI_file>`_, from Paste and Pyramid legacy. To avoid copy-pasted configuration settings

.. _configuration-structure:

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

See :download:`base.ini <../../../websauna/conf/base.ini>`.

.. _development.ini:

development.ini
---------------

This is the configuration file for running the local development server

* No outgoing email

* Celery jobs are executed eagerly, no need to run Celery process

* No backups

* Development databases

* Enable all Pyramid debug options.

* Enable :term:`pyramid_debugtoolbar`.

See :download:`development.ini <../../../websauna/conf/development.ini>`.

.. _test.ini:

test.ini
--------

Settings for running unit tests

* No outgoing email

* Test database

* Jinja templates in strict mode (raise exception on missing template variable)

See :download:`development.ini <../../../websauna/conf/test.ini>`.

.. _production.ini:

production.ini
--------------

Settings for running Websauna on production server.

* Mail out

* Production database

* No debugging

* Cached static files

See :download:`production.ini <../../../websauna/conf/production.ini>`.

.. _staging.ini:

staging.ini
-----------

Same as `production.ini`, but with staging secrets, so that you can use different API credentials for a staging server and production server.

secrets
-------

See :doc:`secrets documentation <../narrative/misc/secrets>`.

Configuration inclusion
=======================

For examples see any INI file produced by :term:`scaffold`.

.. note ::

    Configuration inclusion system will be phased out in the future versions to be replaced with more generic configuration solution.

Example ``continuos-integration.ini`` which extends other INI files and overrides some settings::


    [includes]
    include_ini_files =
        resource://websauna/conf/test.ini
        resource://websauna/conf/base.ini

    [app:main]
    use = egg:websauna
    websauna.init = websauna.Initializer
    sqlalchemy.url = postgres://ci:ci:@localhost:5434/test


Websauna configuration variables
================================

The following variables are available.

websauna.activate_redirect
--------------------------

The Pyramid route name where the user is taken after clicking the email activation link.

See :py:meth:`websauna.system.user.registrationservice.DefaultRegistrationService.activate_by_email`.

Default: ``registration_complete``.

.. _websauna.admin_as_superuser:

websauna.admin_as_superuser
---------------------------

All members in admin group are also superusers.

.. note ::

    It is only safe to enable this settings on your local computer. Never enable this in an environment which can be accessed over Internet.

Default: ``true`` in :ref:`development.ini`, ``false`` otherwise.

See also :ref:`websauna.superusers`.

websauna.cachebust
------------------

Use Pyramid cache busting mechanism when serving static assets.

This option controls whether or not static assets are served in production deployment or CDN mode.

Enable this in production deployments to have never expiring URLs for all items referred by ``request.static_url()`` or ``{{ 'xxx'|static_url }}`` in templates.

URLs are tagged by file MD5 hash. If the source asset file (CSS, JS image) changes a new URL is generated, invalidating the cache.

Default:: ``false``.

More info

* http://docs.pylonsproject.org/projects/pyramid/en/1.6-branch/narr/assets.html#cache-busting-and-asset-overrides

websauna.activation_token_expiry_seconds
----------------------------------------

How quickly email activation and password reset token turns sour.

Default: 24 hours

websauna.allow_email_auth
-------------------------

Allow users to sign in by email (besides username).

Default: ``true``.

websauna.allowed_hosts
----------------------

Whitespace separated list of hostnames this site is allowed to respond.

This is a security feature preventing direct IP access of sites.

Set this to list of your production domain names::

    websauna.allowed_hosts =
        libertymusicstore.net
        upload.libertymusicstore.net

Default: ``localhost``.

websauna.allow_inactive_login
-----------------------------

Allow users who have not verified their email to sign in.

Default: ``false``.

.. _websauna.cache_max_age_seconds:

websauna.cache_max_age_seconds
------------------------------

How long :ref:`static assets <static>` are cached. Any non-zero value enables caching busting.

Default: 0 (development), 2 weeks (production)

websauna.autologin
------------------

Automatically sign in the user after completing the sign up form.

See :py:meth:`websauna.systme.user.registrationservice.DefaultRegistrationService.sign_up`.

Default: ``false``.

.. _websauna.celery_config:

websauna.celery_config
----------------------

A Python dictionary to configure Celery.

`See Celery manual for configuration <http://docs.celeryproject.org/en/master/userguide/configuration.html>`_.

See :ref:`ws-celery`.

See :py:meth:`websauna.system.Initializer.configure_tasks`.

See :ref:`tasks` documentation.

Example:

.. code-block:: ini

    [app:main]
    # ...
    websauna.celery_config =
        {
            "broker_url": "redis://localhost:6379/3",
            "accept_content": ['json'],
            "task_always_eager": False,
            "beat_schedule": {
                # config.scan() scans a Python module
                # and picks up a celery task named test_task
                "test_task": {
                    "task": "foobar",
                    "schedule": timedelta(seconds=1)
                }
            }
        }


websauna.error_test_trigger
---------------------------

If set enable a view at path ``/error-trigger`` that generates a runtime error.

You can use this view to generate an error and see that your logging and error monitoring system functions correctly.

Default: ``false``.

websauna.global_config
----------------------

This is a reference to ``global_config`` object which is used to initialize Pyramid application. It is a dictionary. Example::

    {'__file__': '/Users/mikko/code/trees/trees/development.ini', 'here': '/Users/mikko/code/trees/trees'}


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

websauna.log_internal_server_error
----------------------------------

When the user is being served 500 internal server error (:py:func:`websauna.system.core.views.internalservererror.internal_server_error`) send the error traceback to standard Python ``logger``.

Disabling this is most useful for testing where you do not want to see tracebacks polluting your log output.

Default: ``true``

websauna.login_after_activation
-------------------------------

Are users automatically logged in after clicking the email verification link.

See :py:meth:`websauna.system.user.registrationservice.DefaultRegistrationService.activate_by_email`.

Default: ``false``.

websauna.login_redirect
-----------------------

The Pyramid route name where the user is redirected after successful login.

See :py:meth:`websauna.system.user.loginservice.DefaultLoginService.authenticate_user`.

Default: ``home``.

websauna.logout_redirect
------------------------

The Pyramid route name where the user is redirected after successful login.

See :py:meth:`websauna.system.user.loginservice.DefaultLoginService.logout`.

Default: ``login``.

.. _websauna.mailer:

websauna.mailer
---------------

Choose the mail backend class.

Available options

* ``websauna.system.mail.mailer.StdoutMailer`` - dump email to stdout. Default in :term:`development`.

* ``mail`` - use the SMTP configured for pyramid_mailer. Default in :term:`production`.

* ``pyramid_mailer.mailer.DummyMailer`` - No any kind of mail out. Default in :term:`testing`.

See also :py:meth:`websauna.system.Initializer.configure_mail`.

See also below ``pyramid_mailer`` for configuring the actual mail server details.

websauna.require_activation
---------------------------

Do user need to verify their email before they can sign in.

See :py:meth:`websauna.system.user.registrationservice.DefaultRegistrationService.sign_up`.

Default: ``true``.

websauna.request_password_reset_redirect
----------------------------------------

The pyramid route name where the user is taken after submitting a password reset request.

See :py:meth:`websauna.system.user.credentialactivityservice.DefaultCredentialActivityService.create_forgot_password_request`.

Default: ``login``

websauna.reset_password_redirect
--------------------------------

The pyramid route name where the user is taken after performing a password reset via email.

See :py:meth:`websauna.system.user.credentialactivityservice.DefaultCredentialActivityService.create_forgot_password_request`.

Default: ``login``

.. _websauna.sample_html_email:

websauna.sample_html_email
--------------------------

Enable ``/sample-html-email`` view for testing HTML email looks.

Default: true in  :ref:`development.ini`, false otherwise


.. _websauna.sanity_check:

websauna.sanity_check
---------------------

Perform database sanity check after the startup. This will check all models have corresponding tables and columns in the database and there are no unsynced models.

Disabled for testing and various command line commands on a call to :py:func:`websauna.system.devop.cmdline.init_websauna`.

See also :py:meth:`websauna.system.Initializer.sanity_check`.

Default: ``true``



websauna.social_logins
----------------------

List of configured social logins, or federated authentication, methods.

* List can be space or new line separated

* Each social login corresponds one entry in secrets INI file

Example value:

.. code-block:: ini

    websauna.social_logins =
        facebook
        twitter

In which case your secrets INI would contain:

.. code-block:: ini

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

.. _websauna.secrets_file:

websauna.secrets_file
---------------------

Secrets file for API keys and tokens. :doc:`Read secrets documentation for more information <../narrative/misc/secrets>`.

The value is in URL format ``resource://PYTHON_PACKAGE_NAME/PATH_TO_INI_FILE_INSIDE_PACKAGE``.

Default value: ``resource://websauna/development-secrets.ini``.

websauna.secrets_strict
-----------------------

If environment variables are missing in the secrets INI file interpolation, raise an exception.

See :py:func:`websauna.utils.secrets.read_ini_secrets`.

Default value: ``true``

websauna.site_id
----------------

An alphanumeric id for the site. If multiple sites are running on the same resources this can be used to discriminate between sites.

For example backup scripts tags backup archives with this identifier.

Default value: project name + "_prod"

websauna.site_name
------------------

See :py:func:`websauna.system.core.vars.site_name`.

websauna.site_url
-----------------

See :py:func:`websauna.system.core.vars.site_url`.

Default: No default, must be set.

websauna.site_tag_line
----------------------

See :py:func:`websauna.system.core.vars.site_tag_line`.

Default: No default, must be set.


websauna.site_email_prefix
--------------------------

See :py:func:`websauna.system.core.vars.site_email_prefix`.

Default: No default, must be set.

websauna.site_time_zone
-----------------------

See :py:func:`websauna.system.core.vars.site_time_zone`.

Default: :term:`UTC`.

.. _websauna.superusers:

websauna.superusers
-------------------

List of superuser emails or usernames. Add your username on this list to make it super user.

Example:

.. code-block:: ini

    websauna.superusers =
        admin
        mikko@example.com

.. warning::

    Superuser permission allows executing arbitrary code on the server.

More information

* See :doc:`Notebook documentation <../narrative/misc/notebook>`

.. _websauna.template_debugger:

websauna.template_debugger
--------------------------

Which debugger to invoke when hitting ``{{ debug() }}`` inside a page template.

See :ref:`debug <var-debug>` template variable.

Default: ``pdb.set_trace`` in :ref:`development.ini`, otherwise turned off.

websauna.test_web_server_port
-----------------------------

A port where to run the test server for functional tests.

This is used by ``web_server`` py.test test fixture.

Default: ``8521``.


Configuration from other packages
=================================

.. _celery-config:

Celery
------

Websauna uses :term:`pyramid_celery` which allows you to put :term:`Celery` configuration variables to a INI file.

For example see Websauna base.ini. `For more information see Celery configuration <http://docs.celeryproject.org/en/latest/configuration.html>`_.

Alembic
-------

`See Alembic <http://alembic.readthedocs.org/en/latest/tutorial.html#editing-the-ini-file>`_.

pyramid_redis
-------------

`See pyramid_redis <http://pyramid-redis-sessions.readthedocs.org/en/latest/gettingstarted.html>`_.

.. _pyramid.mailer:

pyramid_mailer
--------------

``pyramid_mailer`` is underlying component used by :ref:`email out <mail>`. Also see :ref:`websauna.mailer` setting.

`See pyramid_mailer configuration <http://docs.pylonsproject.org/projects/pyramid-mailer/en/latest/#configuration>`_.

mail.default_sender_name
++++++++++++++++++++++++

Set up envelope name for the sender.

Example:

.. code-block:: ini

    mail.default_sender = no-reply@example.com
    mail.default_sender_name = Example Technologies

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
