=============
Configuration
=============

Websauna uses `INI-based configuration files <https://en.wikipedia.org/wiki/INI_file>`_, stemming from Paste and Pyramid legacy. Each command line command or WSGI web application launch module takes one of these INI files as an input. INI file tells

Configuration structure
=======================

Websauna INI configuration files are extensible. You can include base INI configuration files in your settings file from file system and other Python packages.

Websauna package defines three configuration files which you should use

Configuration inclusion
=======================

.. note ::

    Configuraiton inclusion system will be phased out in the future versions to be replaced with more generic configuration solution.

Configuration variables
=======================

The following variables are available

websauna.superuser
-----------------------

List of superuser emails or usernames. Add your username on this list to make it super user.

Example::

    websauna.superuser =
        admin
        mikko@example.com

.. warning::

    Superuser permission allows executing arbitrary code on the server.


websauna.global_config
---------------------------

This is a reference to ``global_config`` object which is used to initialize Pyramid application. It is a dictionary. Example::

    {'__file__': '/Users/mikko/code/trees/trees/development.ini', 'here': '/Users/mikko/code/trees/trees'}


websauna.sanity_check
--------------------------

Perform database sanity check after the startup. This will check all models have corresponding tables and columns in the database and there are no unsynced models.

Disabled for testing.

Default: ``true``

Configuration variables from other packages
===========================================

* Paste

* Alembic

* pyramid_redis

* sqlalchemy

* Python logging