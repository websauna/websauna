.. _sql-troubleshooting:

===================
Troubleshooting SQL
===================

.. contents:: :local:

Introduction
============

In this chapter we have collected instructions to troubleshoot issues with :term:`SQL`, :term:`SQLAlchemy` and databases.

Turning on SQLAlchemy logging
=============================

SQLAlchemy can be made verbosely echo all SQL statements it executes. This way you can replay issues in a :ref:`ws-db-shell` by hand and manually inspect the state of the database and transaction between each SQL statement.

Do the following to turn on the logging.

Edit :ref:`development.ini` and set echo variable for your connection:

.. code-block:: ini

    [app:main]
    # ...
    sqlalchemy.url = # ...
    sqlalchemy.echo = true

In the same file, add a section to make SQLAlchemy logging verbose:

.. code-block:: ini

    [logger_sqlalchemy]
    level = DEBUG
    handlers =
    qualname = sqlalchemy

