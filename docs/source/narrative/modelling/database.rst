==============
Using database
==============

SQL database
============

Websaunan uses an SQL database. SQLAlchemy object relations mapping (ORM) library is used to create Python classes representing the model of data. From these models corresponding SQL database tables are created in the database.

By default, PostgreSQL database software is recommended, though Websauna should be compatible with all databases supported by SQLAlchemy

Accessing database session
--------------------------

All database operations are done through SQLAlchemy session.

Session in a HTTP request
+++++++++++++++++++++++++

Session in a command line application
+++++++++++++++++++++++++++++++++++++

You can get a access to the database session through a :py:class:`websauna.system.Initializer` instance exposed through a constructed WSGI application:

    TODO

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

:term`pyramid_debugtoolbar` gives various information regarding executed SQL queries during the page rendering.

PostgreSQL specific
===================

The default :py:class:`websauna.system.user.usermixin` uses the following column types might not be available on other database systems

* :py:class:`sqlalchemy.dialects.postgresql.JSONB` (can be downgraded to :py:class:`sqlalchemy.dialects.postgresql.JSON` for older PostgreSQL version compatibility)

* :py:class:`sqlalchemy.dialects.postgresql.INET` - IPv4 and IPv6 addresses

* :py:class:`sqlalchemy.dialects.postgresql.UUID` - IPv4 and IPv6 addresses

At the moment

* Either Websauna must be patched with emulation layer for these columns for other database systems. It should be relative easy to emulate these with text columns and custom SQLAlchemy types

* Use your custom user model without these fields
