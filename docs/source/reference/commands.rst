Command line commands
=====================

All command line commands take ``ini`` settings as their first argument.

.. contents:: :local:

ws-shell
--------

Open `IPython terminal shell <https://github.com/dbcli/pgcli>`_ prompt for your application.
This also imports all your configured models by default, creates initial database session, so you are good to go to manipulate your application.

Example::

    ws-shell development.ini

.. _ws-db-shell:

ws-db-shell
-----------

*ws-db-shell* command opens `pgcli <https://github.com/dbcli/pgcli>`_ command line tool for the configured PostgreSQL database.

Example::

    ws-db-shell development.ini

Then you can manipulate database directly using PostgreSQL commands. Example how to list tables::

    websauna> \dt

Example results::

    +----------+----------------+--------+---------+
    | Schema   | Name           | Type   | Owner   |
    |----------+----------------+--------+---------|
    | public   | activation     | table  | moo     |
    | public   | distributors   | table  | moo     |
    | public   | foobar         | table  | moo     |
    | public   | group          | table  | moo     |
    | public   | referrals      | table  | moo     |
    | public   | shortened_urls | table  | moo     |
    | public   | user_group     | table  | moo     |
    | public   | users          | table  | moo     |
    +----------+----------------+--------+---------+
    SELECT 8

How to check table schema for table ``review``::

    trees> \d+ review

Example output::

    +-------------+--------------------------+-----------------------------------------------------+-----------+----------------+---------------+
    | Column      | Type                     | Modifiers                                           | Storage   |   Stats target |   Description |
    |-------------+--------------------------+-----------------------------------------------------+-----------+----------------+---------------|
    | id          | integer                  | not null default nextval('review_id_seq'::regclass) | plain     |         <null> |        <null> |
    | created_at  | timestamp with time zone |                                                     | plain     |         <null> |        <null> |
    | updated_at  | timestamp with time zone |                                                     | plain     |         <null> |        <null> |
    | customer_id | integer                  |                                                     | plain     |         <null> |        <null> |
    | delivery_id | integer                  |                                                     | plain     |         <null> |        <null> |
    | uuid        | uuid                     |                                                     | plain     |         <null> |        <null> |
    | product     | character varying(32)    |                                                     | extended  |         <null> |        <null> |
    | rating      | integer                  |                                                     | plain     |         <null> |        <null> |
    | review_data | jsonb                    |                                                     | extended  |         <null> |        <null> |
    +-------------+--------------------------+-----------------------------------------------------+-----------+----------------+---------------+

Then you can exit from pgcli::

    \q


.. _ws-alembic:

ws-alembic
----------

Run Alembic SQLAlchemy database migrations.

For more information see :doc:`migrations <../narrative/ops/databaseops>`.

ws-dump-db
----------

Print PostgreSQL SQL to stdout from the currently configured database. This is equivalent of running ``pg_dump`` command with some arguments against the SQLAlchemy database configured in given INI file.

Example how to backup your development database::

    ws-dump-db development.ini > dump.sql

ws-tweens
---------

Display Pyramid tween stack.

Example::

    ws-tweens development.ini

Example output::

    "pyramid.tweens" config value NOT set (implicitly ordered tweens used)

    Implicit Tween Chain

    Position    Name
    --------    ----
    -           INGRESS
    0           pyramid_debugtoolbar.toolbar_tween_factory
    1           pyramid.tweens.excview_tween_factory
    2           pyramid_tm.tm_tween_factory
    3           websauna.referral.tweens.ReferralCookieTweenFactory
    -           MAIN



ws-sync-db
----------

Create initial tables for the database configuration in the settings file. This equals running :py:meth:`Base.metadata.create_all()` SQLAlchemy command.

Example::

    ws-sync-db development.ini

.. note ::

    Using ws-sync-db is command is not recommended outside testing and prototyping. If you edit your models ws-sync-db doesn't know what to do and you need to drop your tables and data and start over. To have repeatable changes to your databases, use ws-alembic command instead.

Advanced
--------

Command line commands are registered in ``setup.py`` and scripts reside in :py:mod:`websauna.system.devop.scripts`.
