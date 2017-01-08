.. _occ:

==============================
Optimistic concurrency control
==============================

.. contents:: :local:

Introduction
============

Websauna uses :term:`optimistic concurrency control` to eliminate the possibility of :term:`race condition` in your code.

By default, optimistic concurrency control is set up to apply to the primary :term:`SQL` database. Unlike with pessimistic locking, the developer doesn't need to worry creating and managing locks upfront. Instead, a database maintains predicate locking. If a database detects a race condition caused by concurrent transactions, one transaction is let through while the other receives an application level exception. The conflict is then resolved on the application level. This approach is beneficial for applications where the likely of transaction conflicts are rare and it's unlike two concurrent requests write on the same field.

Writing optimistic concurrency control friendly code
====================================================

Serializable transactions isolation level
-----------------------------------------

SQL has support for `transaction isolation levels <https://en.wikipedia.org/wiki/Isolation_%28database_systems%29#Isolation_levels>`_.

With the default PostgreSQL database the default transaction isolation level is set to ``SERIALIZABLE``. This is the highest possible level. This makes sure any code is race condition free by default. Individual views can customize their database session and weaken the isolation requirement for specialized use cases like increasing performance for large reports.

If there is no application support for resolving the transaction conflict, one of the clients get HTTP 500 error page and other goes through. Even in this worst case scenario a user gets reported an error has happened and there is no silent data corruption.

The connection set up is done in :py:func:`websauna.system.model.meta.get_engine()` called by :py:meth:`websauna.system.Initializer.configure_database`.

Different transaction encapsulation patterns
--------------------------------------------

HTTP request and pyramid_tm middleware
++++++++++++++++++++++++++++++++++++++

In Websauna 1 HTTP request = 1 transaction, by default.

If there is a transaction conflict during HTTP request it is automatically retried by ``pyramid_tm`` transaction machinery. Thus, the same HTTP request **may be played twice** on a server under load.

Celery
++++++

Celery tasks can be set automatically retry by using base task :py:class`websauna.system.task.tasks.RetryableTransactionTask`. For more information see :ref:`tasks`.

Using transaction.manager context manager
+++++++++++++++++++++++++++++++++++++++++

You can use ``with TransactionManager()`` thread local in some situations, like command line scripts. This won't retry the transaction in the case of conflict, but it will commit the transaction at the end of the block.

Example:

.. code-block:: python

    def foo(request):
        with request.tm:
            # Do stuff with request.dbsession

In unit tests you can use thread local ``transaction.manager``:

.. code-block:: python

    import transaction


    def test_xxx(dbsession):
        with transaction.manager:
            # Do stuff with dbsession


Note that ``transaction.manager`` **doesn't** work in Celery, as ``transaction.manager`` is a thread local may not be set up correctly.

For more information see `transactions in ZODB book <http://zodb.readthedocs.io/en/latest/transactions.html>`_.

@retryable decorator
--------------------

See below.

Manually splitting up long running transactions
-----------------------------------------------

Long running transactions are bad in OCC systems with a lot of database activity as they might block other transactions for long time or are unlikely to never success. Smaller your transaction isolation sections are, the better.

Below is an example how to split up a long running task (sending out mass email) to separate transactions. We use :py:func:`websauna.system.model.retry.retryable` decorator and wrap each transaction to its own closure function.

.. code-block:: python

    import logging
    import datetime
    from uuid import UUID


    from websauna.system.http import Request
    from websauna.system.mail import send_templated_mail
    from websauna.system.model.retry import ensure_transactionless, retryable
    from websauna.utils.time import now
    from websauna.wallet.views.network import get_asset_resource
    from websauna.system.user.models import User

    logger = logging.getLogger(__name__)


    def send_event_emails(request: Request, before_threshold=36, old_event_threshold=72) -> dict:
        """Send out ICO notification emails.

        This function is to be called by transaction free task (WebsaunaTask) or unit tests. It manages transactions internally.

        :param before_threshold: Send alert if the event is closer than this deadline (hours)

        :param old_event_threshold: Don't send alert if event is past more than this hours (legacy events, reminder not send for some reason)

        :return: {emails: number of emails sends, events: number of events}
        """

        dbsession = request.dbsession

        # Make sure there is no transaction in progress, as we manage transactions ourselves
        ensure_transactionless(transaction_manager=request.tm)

        # We split this long running task to two + N transactions to avoid OCC congestion

        @retryable(tm=request.tm)
        def gather_followers():
            """A transaction that reads all subscribers from the user database."""
            followers = [u.email for u in dbsession.query(User) if get_ico_alert_state(u)]
            return followers

        @retryable(tm=request.tm)
        def gather_upcoming_events():
            """A transaction that gets all event ids that will broadcast a warning."""
            ids = []
            for event in dbsession.query(CalendarEvent).all():
                # Check that outgoing email has not gone out yet for this event
                if not event.notified_at:
                    if event.happens_at - now() <= datetime.timedelta(hours=before_threshold) and now() - event.happens_at <= datetime.timedelta(hours=old_event_threshold):
                        ids.append(event.id)
            return ids

        @retryable(tm=request.tm)
        def mail_about_event(event_id: UUID, follower_emails: list) -> int:
            """Mail about the event. """
            event = dbsession.query(CalendarEvent).get(event_id)
            event.notified_at = now()
            context = {
                "event": event,
            }

            # Here send_templated_mail() triggers only if transaction succesfully commits.
            # TODO: Replace with a proper mass mail function, don't queue individual messages,
            # Example: https://help.mailgun.com/hc/en-us/articles/203068874-How-do-I-send-the-same-message-to-multiple-users-using-Mailgun-

            for email in follower_emails:
                send_templated_mail(request, [email], "email/upcoming_event", context=context)

            return len(follower_emails)

        event_ids = gather_upcoming_events()
        emails = 0

        if event_ids:
            follower_emails = gather_followers()
            for event_id in event_ids:
                emails += mail_about_event(event_id, follower_emails)

        data = {
            "events": len(event_ids),
            "emails": emails,
        }

        logger.info("%s event reminders with %s outgoing emails", data["events"], data["emails"])

        return data

Then you can call this in Celery task:

.. code-block:: python

    @task(name="send_event_emails", bind=True, time_limit=60*30, soft_time_limit=60*15, base=WebsaunaTask)
    def _send_event_emails(self: WebsaunaTask):
        send_event_emails(self.get_request())

Executing actions on successfully commits
-----------------------------------------

See py:meth:`transaction.Transaction.addAfterCommitHook`.

Example:

.. code-block:: python

    def _after_commit_hook():
        print("Executed in web worker process after transaction.commit")

    request.tm.get().addAfterCommitHook(_after_commit_hook)

Do not cache retryable exceptions
---------------------------------

Do not cache database conflict exceptions, as otherwise underlying retry machinery won't work.

Do:

.. code-block:: python

    from websauna.system.model.retry import is_retryable

    try:
        foobar()
    except Exception as e:
        if is_retryable(e):
            raise
        else:
            pass

Don't do:

.. code-block:: python

    try:
        foobar()
    except Exception as e:
        pass

Configuring retry count
-----------------------

TODO

Serializable transaction penalty
--------------------------------

Serializable transactions may incur a performance penalty, measured in couple of percents. There exist several ways to mitigate this

* Read only views

* Proper indexing of data

For more information see

* http://www.postgresql.org/docs/9.5/static/transaction-iso.html

* http://sqlperformance.com/2014/04/t-sql-queries/the-serializable-isolation-level
