.. _occ:

==============================
Optimistic concurrency control
==============================

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

Retrying transaction
--------------------

Executing actions on succesfully commits
----------------------------------------

Do not cache retryable exceptions
---------------------------------

Configuring retry count
-----------------------

Serializable transaction penalty
--------------------------------

Serializable transactions may incur a performance penalty, measured in couple of percents. There exist several ways to mitigate this

* Read only views

* Proper indexing of data

For more information see

* http://www.postgresql.org/docs/9.5/static/transaction-iso.html

* http://sqlperformance.com/2014/04/t-sql-queries/the-serializable-isolation-level
