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
-------------------------

To create a database on Homewbrew / OSX::

    createdb myapp_dev

Creating database on Ubuntu
---------------------------

TODO

Changing database name or authentication details
================================================

If you need to change the default database name or its connection details you can edit :ref:`sqlalchemy.url <sqlalchemy.url>` settings in :term:`development.ini`.

Creating migration scripts
==========================

Websauna stores data in SQL databases in tables. When these tables are changed, the database must be instructed to perform the changes. The change is recorded as a migration script which can repeatably run across several computers (coworkers, different servers). Initially you will need the migration scripts to create database tables for user and groups of your website.

To do this we use :ref:`ws-alembic` command::

    TODO