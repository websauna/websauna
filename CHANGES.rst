Changelog for Websauna
======================


1.0a12 (2018-11-01)
-------------------

- Replace deprecated logger.warn with logger.warning.

- Replace deprecated pyramid.session.check_csrf_token with pyramid.csrf.check_csrf_token.

- Upgrades transaction to version 2.4.0.

- Closes `Issue #206`_: New implementation of ThreadTransactionManager breaks websauna.

- Upgrades Pyramid to version 1.10.


1.0a11 (2018-10-10)
-------------------

- Support pyramid_notebook 0.3.0.

- Support pgcli 2.0.0.

- Reorganize package extras, adding a docs session.

- Closes `Issue #195`_: Documentation epub does not open on iBooks.


1.0a10 (2018-09-23)
-------------------

- Closes `Issue #179`_: Support for Celery 4.2.0.

- Closes `Issue #193`_: Using celery.group raises AttributeError: 'WebsaunaLoader' object has no attribute 'request'.

- Adds support to Python 3.7.0.

- Remove support to Sqlite.

- Closes `Issue #171`_: Replace Websauna JSONB usage with sqlalchemy.dialects.postgresql.JSONB.

- Reorganize tests.


1.0a9 (2018-04-30)
------------------

- Pin Celery to version 4.1.0.


1.0a8 (2018-04-21)
------------------

- Closes `Issue #165`_: Fix path to breadcrumbs template.

- Closes `Issue #167`_: Fix 'autologin' and 'require_activation' settings.

- Closes `Issue #169`_: Reflective sitemap reuses dbsession.

- Closes `Issue #170`_: Enums now support distinct names/values.

- Do not ignore the *prefix* setting in get_engine.

- Allow using settings in celery configs.

- Support setting transaction isolation level.

- Sqlite support is being deprecated, will be removed in 1.0b1.


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
.. _`Issue #165`: https://github.com/websauna/websauna/issues/165
.. _`Issue #167`: https://github.com/websauna/websauna/issues/167
.. _`Issue #169`: https://github.com/websauna/websauna/issues/169
.. _`Issue #170`: https://github.com/websauna/websauna/issues/170
.. _`Issue #171`: https://github.com/websauna/websauna/issues/171
.. _`Issue #179`: https://github.com/websauna/websauna/issues/179
.. _`Issue #193`: https://github.com/websauna/websauna/issues/193
.. _`Issue #195`: https://github.com/websauna/websauna/issues/195
.. _`Issue #206`: https://github.com/websauna/websauna/issues/206
