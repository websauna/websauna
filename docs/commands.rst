Command line commands
=====================

All command line commands take ``ini`` settings as their first argument.

.. contents:: :local:

ws-sync-db
----------

Create tables for the database configuration in the settigs file.

Example::

    ws-sync-db development.ini


ws-shell
--------

Open `IPython terminal shell <https://github.com/dbcli/pgcli>`_ prompt for your application.
This also imports all your configured models by default, creates initial database session, so you are good to go to manipulate your application.

Example::

    ws-shell development.ini

ws-db-shell
-----------

Open `pgcli <\>`_ command line tool for the configured PostgreSQL database.

Example::

    ws-db-shell development.ini

Then you can manipulate database directly using PostgreSQL commands. Example how to list tables::

    pyramid_web20> \dt

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



