=====================
Command line commands
=====================

Most Websauna commands take the configuration file, like :term:`development.ini`, as their first argument. The command will be different depending on if you run it on development, staging or production environment.

.. contents:: :local:

Available commands
==================

.. _ws-pserve:

ws-pserve
---------

Run a development web server on your local computer.

Example:

.. code-block:: console

    ws-pserve ws://development.ini --reload


This is a wrapped around Pyramid `pserve <http://docs.pylonsproject.org/projects/pyramid/en/latest/pscripts/pserve.html?highlight=pserve>`_ command.

.. warning:: This command is deprecated and will be removed in a future version of Websauna.


ws-proutes
----------

Get an overview of all registered routes.

Example:

.. code-block:: console

    ws-proutes ws://development.ini


This is a wrapper around Pyramid's `proutes <http://docs.pylonsproject.org/projects/pyramid/en/latest/pscripts/proutes.html>`_ command.

.. warning:: This command is deprecated and will be removed in a future version of Websauna.


.. _ws-celery:

ws-celery
---------

A wrapper command for `celery command <http://docs.celeryproject.org/en/latest/userguide/monitoring.html?highlight=command#workers>`_, supporting config inclusion mechanism.

See :ref:`tasks`.

.. _ws-shell:

ws-shell
--------

Open `IPython terminal shell <http://ipython.readthedocs.org/en/stable/index.html>`_ prompt for interactive Python session with your application. It imports all your configured models by default, creates initial database session, so you are good to go to manipulate your application.

Example:

.. code-block:: console

    ws-shell ws://development.ini


.. _ws-db-shell:

ws-db-shell
-----------

*ws-db-shell* command opens `pgcli <https://github.com/dbcli/pgcli>`_ command line tool for the configured PostgreSQL database.

Example:

.. code-block:: console

    ws-db-shell ws://development.ini

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


*pgcli* configuration file is in ``/.config/pgcli/config``. For example, `to disable less paging <https://groups.google.com/forum/#!topic/pgcli/THL03KlFIdo>`_ you can add::

    pager = cat

.. _ws-create-table:

ws-create-table
---------------

Print out :term:`SQL` ``CREATE TABLE`` statements needed to construct currently configured models.

Example:

.. code-block:: console

    ws-create-table ws://development.ini


.. _ws-alembic:

ws-alembic
----------

Run Alembic SQLAlchemy database migrations.

For more information see :doc:`migrations <../narrative/ops/migrations>`.

ws-dump-db
----------

Print PostgreSQL SQL to stdout from the currently configured database. This is equivalent of running ``pg_dump`` command with some arguments against the SQLAlchemy database configured in given INI file.

Example how to backup your development database:

.. code-block:: console

    ws-dump-db ws://development.ini > dump.sql

Example how to get a remote production database to your local computer:

.. code-block:: console

    ssh myserver -C "sudo -i -u wsgi /srv/pyramid/company.application/venv/bin/ws-dump-db ws:///srv/pyramid/company.application/company/application/conf/generated.ini" > dump.sql

ws-sanity-check
---------------

Performs database sanity check.

Exit values:

    * 0: All ok

    * 10: Sanity check failed - we have unrun migrations

    * Any other value: Launch failed due to Python exception or similar

Example:

.. code-block:: console

    ws-sanity-check ws://conf/production.ini


.. _ws-tweens:

ws-tweens
---------

Display Pyramid tween stack.

Example:

.. code-block:: console

    ws-tweens ws://development.ini


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


.. warning:: This command is deprecated and will be removed in a future version of Websauna.


ws-sync-db
----------

Create initial tables for the database configuration in the settings file. This equals running :py:meth:`Base.metadata.create_all()` SQLAlchemy command.

Example:

.. code-block:: console

    ws-sync-db ws://development.ini

.. note:: Using ws-sync-db is command is not recommended outside testing and prototyping. If you edit your models ws-sync-db doesn't know what to do and you need to drop your tables and data and start over. To have repeatable changes to your databases, use ws-alembic command instead.

ws-create-user
--------------

Create a new site user. If this user is the first user of the site the user becomes an administrator.

.. note:: Recommended only to be used on a local development site. For a production sites for the first user do a normal email sign up.

Example:

.. code-block:: console

    ws-create-user ws://development.ini myemail@example.com


.. note:: It is possible to give password as the third command line argument, but this is not recommended because the password is recorded to your shell history.


.. _ws-collect-static:

ws-collect-static
-----------------

Read through all configured static views and compile their assets to ``collected-static`` folder.

This needs to be run on production and staging server where one has configured cache busting policy.

Example:

.. code-block:: console

    ws-collect-static ws://conf/production.ini

For more information see :ref:`static assets <static>`.

Advanced
========

Pyramid p* commands
-------------------

See `p* commands in Pyramid documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/index.html#p-scripts-documentation>`_.

Command registry
----------------

Command line commands are registered in ``setup.py`` and scripts reside in :py:mod:`websauna.system.devop.scripts`.

Creating your own commands
--------------------------

For examples see e.g. :py:mod:`websauna.system.devop.scripts.createuser` and :py:mod:`websauna.system.devop.cmdline`.
