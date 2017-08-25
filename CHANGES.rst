Changelog for Websauna
======================


1.0a5 (unreleased)
------------------

- Enable Twitter login

- Use proper JSON field for ``User.user_data`` in the admin interfaces

- ``RetryableTransactionTask`` now correctly retries the Celery tasks. Previously the second attempt did not get full Celery task context meaning the tasks usually failed. Furthermore we no longer use pyramid_tm inside Celery tasks, but Websauna specific retryable decorator.

- Update jQuery to 3.1.1. Old jQuery is kept in the source tree for backwards compatibility.

- Added :py:class:`websauna.system.crud.views.CSVListing` and user CSV export

- :ref:`ws-shell` `request.application_url` comes from :ref:`websauna.site_url` setting and does not default to localhost

- Write the session cookie and Redis session data only if something was stored in the session. This makes it more scalable to serve anonymous pages, as one does not need to reset the cookie on every crawling request.

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

