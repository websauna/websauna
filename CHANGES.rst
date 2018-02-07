Changelog for Websauna
======================


1.0a7 (2018-02-07)
------------------

- Closes `Issue #162`_: Enforce timezone to be 'True' on UTCDateTime.


1.0a6 (2018-01-29)
------------------

- Closes `Issue #155`_: AttributeError: 'super' has no attribute update_first_login_social_data on first user login.

- Closes `Issue #157`_: Changing User's Username / Email in Admin Crashes.

- Added code style validations.

- Correctly allow overriding title for listing views.

- Dropped Python 3.4 support.


1.0a5 (2017-12-12)
------------------

- Added support for Pyramid 1.9

- Added support for Python 3.6

- Closes `Issue #29`_: Allow setting redis.sessions.url and websauna.celery_config from secrets file

- Refactor SocialLoginMapper: separate ABC and Interface to their own classes.

- Enable Twitter login

- Use proper JSON field for ``User.user_data`` in the admin interfaces

- ``RetryableTransactionTask`` now correctly retries the Celery tasks. Previously the second attempt did not get full Celery task context meaning the tasks usually failed. Furthermore we no longer use pyramid_tm inside Celery tasks, but Websauna specific retryable decorator.

- Update jQuery to 3.1.1. Old jQuery is kept in the source tree for backwards compatibility.

- Added :py:class:`websauna.system.crud.views.CSVListing` and user CSV export

- :ref:`ws-shell` `request.application_url` comes from :ref:`websauna.site_url` setting and does not default to localhost

- Write the session cookie and Redis session data only if something was stored in the session. This makes it more scalable to serve anonymous pages, as one does not need to reset the cookie on every crawling request.

- Use `typing <https://pypi.python.org/pypi/typing>`_ instead of `backports.typing <https://pypi.python.org/pypi/backports.typing>`_ for Python 3.4.

- Fixes `Issue #29`_: Replace pcreate with cookiecutter.


1.0a4 (2017-01-07)
------------------

- Reworked the rules for JSONB columns and their default values. See `JSON column documentation for more information <https://websauna.org/docs/narrative/modelling/json.html>`_.

- Fix user.user_data not correctly populated when user was created from command line, as reported by @mazz


1.0a3 (2016-12-13)
------------------

- Require Python 3.5.2 or newer on 3.5.x series, as 3.5.1 contains a bug in typing module preventing Websauna to run ( https://gist.github.com/mazz/b31fb5a89605548868a91abb91f8faf8 ) - reported by @mazz


1.0a1 (2016-12-08)
------------------

- Life sucks and then you die. But Websauna is out: https://www.youtube.com/watch?v=AOfiziY-htU


.. _`Issue #29`: https://github.com/websauna/websauna/issues/29
.. _`Issue #145`: https://github.com/websauna/websauna/issues/145
.. _`Issue #155`: https://github.com/websauna/websauna/issues/155
.. _`Issue #157`: https://github.com/websauna/websauna/issues/157
.. _`Issue #162`: https://github.com/websauna/websauna/issues/162
