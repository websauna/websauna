=====================
Setting up a database
=====================

Websauna users SQL database for its primary persistant data storage. This tutorial and recommendation suggest you to use PostgreSQL database.

To get Websauna application started you need to

* Create a database inside PostgreSQL installation

* Have a user which can connect database

* Create Websauna initial database table creation scripts

* Run these scripts against your local database

Creating the database
=====================

The default local development database name is ``myapp_dev`` where ``myapp`` is replaced with your application name.

Creating database on OSX
------------------------

To create a database on Homewbrew / OSX use ``createdb`` PostgreSQL command::

    createdb myapp_dev

Creating database on Ubuntu
---------------------------

You need to sudo to ``postgres`` user to run any :term:`PostgreSQL` commands:

    sudo -u postgres createdb myapp_dev

Changing database name or authentication details
================================================

If you need to change the default database name or its connection details you can edit :ref:`sqlalchemy.url <sqlalchemy.url>` settings in :term:`development.ini`.

Creating migration scripts
==========================

.. note ::

    This will be covered later in detail.

Websauna stores data in SQL databases in tables. When these tables are changed, the database must be instructed to perform the changes. The change is recorded as a migration script which can repeatably run across several computers (coworkers, different servers). Initially you will need the migration scripts to create database tables for user and groups of your website.

To do this we use :ref:`ws-alembic` command inside ``myapp`` folder::

    cd myapp
    ws-alembic -c conf/development.ini -x packages=all revision --auto -m "Initial migration"

This creates migration script for the default ``user`` and ``groups`` SQL tables.

Now you should see migration scripts created with a hashed name::

    ls alembic/versions
    ...
    -rw-r--r-- 1 moo staff 3610 Jan  6 20:52 8513e50cda41_initial_migration.py

Running the migration script
============================

Migration script is a repeatable and can be run against multiple database. First you need to run it against the database on your local development computer::

    ws-alembic -c conf/development.ini -x packages=all upgrade head

Checking what's in your database
================================

You can use :ref:`ws-db-shell` to open a *pgcli* prompt to explore your PostgreSQL database::

    ws-db-shell conf/development.ini

    wattcoin_dev> \dt
    +----------+--------------------------+--------+---------+
    | Schema   | Name                     | Type   | Owner   |
    |----------+--------------------------+--------+---------|
    | public   | activation               | table  | moo     |
    | public   | alembic_history_myapp    | table  | moo     |
    | public   | group                    | table  | moo     |
    | public   | usergroup                | table  | moo     |
    | public   | users                    | table  | moo     |

