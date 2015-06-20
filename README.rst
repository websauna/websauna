Websauna is a a Python web framework aimed for building consumer and community websites.

Goal
====

* Clone this repository and you get a running Pyramid website out of the box

* Log in and sign up using Facebook, Github or email confirmation

* Start extending the site in your own project step-by-step

Benefits
========

* Running unit tests using PostgreSQL, optimized for speed

* Setting up unit tests

This is so-called *opionated* project where the authors have chosen best of their breeds components based on their long experience in web development. The chosen component set might not suit for your use case. However if you have no or little prior web development experience this project provides you somewhat sane defaults to get you started fast, cutting down the initial development time signicantly.

Even if you are experienced developer this project may offer you some best practices you can copy-paste to your own projects.

Stack
=====

Chosen set of components

Backend
-------

* Python 3.4

* Pyramid 1.5.1 web framework

* Deform form framework

* PostgreSQL with JSONB fields for NoSQL-like schemaless data

* Horus

* `Authomatic <http://peterhudec.github.io/authomatic/>`_ - Social log ins

Frontend
--------

* Bootstrap (CDN distributed)

* jQuery (CDN distributed)

* FontAwesome icons

Actual tested component versions may be found in the continuous integration test suite.

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