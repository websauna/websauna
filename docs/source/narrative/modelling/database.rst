.. _persistent:

================
Database and SQL
================

.. contents:: :local:

Introduction
============

Websauna uses an :term:`SQL` database. :term:`SQLAlchemy` object relations mapping (ORM) library is used to create Python classes representing the model of data. From these models corresponding SQL database tables are created in the database.

By default, :term:`PostgreSQL` database software is recommended, though Websauna is compatible, but not tested, with all databases supported by SQLAlchemy.

PostgreSQL vs. SQLite
=====================

Websauna supports both PostgreSQL and SQLite databases. Here is short summary what you should use.

SQLite
------

Pros

* No software installation needed

* Good for local development when starting out

Cons

* Cannot handle multiple users

* No decimal support: cannot do local development in money or accounting oriented applications

* No datetime support

PostgreSQL
----------

Pros

* Best open source SQL database out there, don't look further

Cons

* An order of magnitude harder to get started with compared to SQLite


.. _dbsession:

Accessing database session
==========================

All database operations are done through a SQLAlchemy session (:py:class:`sqlalchemy.orm.Session`).

Session in a HTTP request processing
------------------------------------

Session is exposed as :py:attr:`websauna.system.http.Request.dbsession` attribute::

    def my_view(request):
        dbsession = request.dbsession
        user = dbsession.query(User).get(1)

``request.dbsession`` transaction is bound to HTTP request lifecycle. If HTTP request succeeds, the transaction is committed. If HTTP request fails due to a raised exception, but not due to error value return from view, the transaction is rolled back and nothing is written into a database.

Session from other SQLAlchemy model instances
---------------------------------------------

This is a common pattern when writing model APIs. You have an existing database object and you want to query related objects. In this case you can grab the session from the existing object using :py:meth:`sqlalchemy.orm.Session.object_session`.

Example::

    from sqlalchemy.orm import Session


    class UserOwnedAccount(Base):

        # ...

        @classmethod
        def create_for_user(cls, user, asset):
            dbsession = Session.object_session(user)
            account = Account(asset=asset)
            dbsession.flush()
            uoa = UserOwnedAccount(user=user, account=account)
            return uoa

Session in a command line application
-------------------------------------

Use :py:func:`websauna.system.devop.cmdline.init_websauna` to create a dummy :py:class:`websauna.system.http.Request` object. It will expose request in similar fashion as for HTTP request.

You need to manually manage transaction lifecycle as there is no real HTTP request lifecycle::

    import transaction

    request = init_websauna("conf/development.ini")
    with transaction.manager:
        user = dbsession.query(User).get(1)
        user.full_name = "Foo Bar"


Session in tasks
----------------

For :doc:`asynchronous tasks <../misc/task>` session is available through :py:class:`websauna.system.http.Request` given as an compulsory argument for tasks. Transaction-aware tasks maintain their own transction lifecycle and there is no need to invoke transaction manager or commit manually::

    @test_celery_app.task(base=TransactionalTask)
    def sample_task(request, user_id):
        dbsession = request.dbsession
        User = get_user_class(registry)
        u = dbsession.query(User).get(user_id)
        u.username = "set by celery"

Session in shell
----------------

Session in shell (:term:`notebook`, :ref:`ws-shell`) is available through ``dbsession`` variable. You need to commit the transaction at the end of your shell session using :py:func:`transaction.commit`.

.. code-block:: pycon

    >>> u = dbsession.query(User).get(1)
    <User-1>

    >>> u.full_name = "Jon Snow"
    ...

    >>> transaction.commit()

Debugging SQL queries
=====================

Debugging by logging
--------------------

You can turn on SQL queries by editing :term:`SQLAlchemy` logging settings in corresponding configuration file like :term:`development.ini`::

    [logger_sqlalchemy]
    level = WARN
    handlers =
    qualname = sqlalchemy.engine
    # "level = INFO" Show SQL queries in the console
    # "level = DEBUG" logs SQL queries and results.
    # "level = WARN" logs neither.  (Recommended for production systems.)

Debugging by pyramid_debugtoolbar
---------------------------------

:term:`pyramid_debugtoolbar` gives various information regarding executed SQL queries during the page rendering.

Custom database sessions
========================

You can override the default factory for ``request.dbsession``.

Example:

.. code-block:: python


    db_session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

    # A function that will resolve dbsession for a request
    def create_test_dbsession(request: Request) -> Session:
        return db_session


    class Initializer(WattcoinInitializer):

            def configure_database(self):
                """Configure database without transaction manager (for test isolation).
                """
                from websauna.system.model.meta import create_transaction_manager_aware_dbsession
                from websauna.system.model.interfaces import ISQLAlchemySessionFactory
                from pyramid.interfaces import IRequest
                self.config.include(".model.meta")
    self.config.registry.registerAdapter(factory=create_test_dbsession, required=(IRequest,), provided=ISQLAlchemySessionFactory)

PostgreSQL specific
===================

The default :py:class:`websauna.system.user.usermixin` uses the following column types might not be available on other database systems

* :py:class:`sqlalchemy.dialects.postgresql.JSONB` (can be downgraded to :py:class:`sqlalchemy.dialects.postgresql.JSON` for older PostgreSQL version compatibility)

* :py:class:`sqlalchemy.dialects.postgresql.INET` - IPv4 and IPv6 addresses

* :py:class:`sqlalchemy.dialects.postgresql.UUID` - IPv4 and IPv6 addresses

At the moment

* Either Websauna must be patched with emulation layer for these columns for other database systems. It should be relative easy to emulate these with text columns and custom SQLAlchemy types

* Use your custom user model without these fields
