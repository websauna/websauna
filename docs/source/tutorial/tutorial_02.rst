===================
Installing Websauna
===================

Websauna is a Python package and installing Python

External dependencies
=====================

To run Websauna on your local computer you need

* PostgreSQL

* Redis

* Python 3.4 or newer

Installing dependencies on OSX
------------------------------

`Install XCode <https://developer.apple.com/xcode/download/>`_.

`Install Homebrew <http://brew.sh/>`_.

Install Python 3.5, Redis, PostgreSQL::

    brew install postgresql redis python3

Installing dependencies on Ubuntu
---------------------------------

TODO

Installing Websauna Python package
==================================

In this guide we create `a Python virtual environment <https://packaging.python.org/en/latest/installing/#creating-virtual-environments>`_ where Websauna package and its Python package dependencies are installed.

Create ``myproject`` folder which contains ``venv`` folder for virtual environment::

    mkdir myproject
    cd myproject
    virtualenv -p python3.5 venv  # We assume you have Python 3.5 installed
    source venv/bin/activate
    pip install websauna

