Websauna is a a Python web framework aimed for building consumer and community websites.

Installation
============

OSX set up
----------

* Install git

* `Install PostgreSQL from Homebrew <https://coderwall.com/p/1mni7w/install-postgresql-on-mountain-lion>`_

* Create database::

    createdb websauna

* Initialize database tables::

    initializedb development.ini

Ubuntu prerequisites
---------------------

* TODO

Starting Python project
-------------------------

* Create virtualenv::

    cd websauna
    virtualenv venv

* Install Python packages::

    pip install -r requirements.txt

* Run the project::

     pserve development.ini --reload

Then navigate to `localhost:6543 <http://localhost:6543>`_ and you should see the front page.

Setting up database
-------------------

Usage
=====

Starting the website.

Customization and overriding defaults
=====================================

To override any parts in ``websauna`` you can do the following.

* Create a new Pyramid project

* Include pip ``requirements.txt`` in your project, change/upgrade versions as needed

* Copy-paste ``main.py``, ``development.ini`` from ``websauna``

* Override necessary parts

* Install your package in the development mode::

    python setup.py develop

Chosen trade offs
=================

Pyramid web framework provides very flexible configuration, but not many defaults components to go with. Thus, the following trade offs have been made with ``websauna``. The main goal of the project is to offer something that works out of the box, not maximum flexibility. So convenience has been chosen over configurability. To override any of these trade offs you might wish to simply fork this project or suggest something clever, so that the project still runs out of the box without going through too many hoops and loops.

* Database is fixed to PostgreSQL

* Cache is fixed to Redis

* Database session management is fixed in ``models.py`` and not configurable

* Template engine is fixed to Jinja 2

* Test runner is fixed to ``py.test``.

Inspiration
===========

* https://gist.github.com/inklesspen/4504383

* http://docs.pylonsproject.org/docs/pyramid/en/latest/tutorials/wiki2/installation.html