===================
Installing Websauna
===================

Websauna is a Python package and installing Python

External dependencies
=====================

To run Websauna on your local computer you need

* :term:`PostgreSQL`

* :term:`Redis`

* :term:`Python` 3.4 or newer

* `libxml2 <http://www.xmlsoft.org/>`_

Installing dependencies on OSX
------------------------------

`Install XCode <https://developer.apple.com/xcode/download/>`_.

`Install Homebrew <http://brew.sh/>`_.

Install Python 3.5, Redis, PostgreSQL:

.. code-block:: console

    brew install postgresql redis python3 libxml2

Make sure PostgreSQL and Redis run on your computer:

.. code-block: console

    brew services start postgresql
    brew services start redis

Make sure ``python3`` command points to Python 3.5:

.. code-block:: console

    python3.5 --version

Should give you::

    Python 3.5.0

If it  use ``brew switch`` command to upgrade

.. code-block:: console

    brew switch python3 python3.5.0   # Or any latest Python 3.5.x version

Installing dependencies on Ubuntu 14.04
---------------------------------------

The following install commands apply for Ubuntu 14.04 and 14.04 only (for example newer Ubuntus come with up-to-date PosgreSQL).

Install the packages with following command:

.. code-block:: shell

    sudo apt install \
        git \
        build-essential \
        libfreetype6-dev \
        libncurses5-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg-dev \
        libpng12-dev \
        gettext \
        python-virtualenv \
        python-software-properties

Install Python 3.5

.. code-block:: shell

    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt -y install python3.5 python3.5-dev

Install Redis

.. code-block:: shell

    sudo apt install redis-server

Install PostgreSQL

.. code-block:: shell

    # http://technobytz.com/how-to-install-postgresql-9-4-in-ubuntu-linux-mint.html
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install postgresql-9.4 libpq-dev

Installing Websauna Python package
==================================

In this guide we create `a Python virtual environment <https://packaging.python.org/en/latest/installing/#creating-virtual-environments>`_ where Websauna package and its Python package dependencies are installed.

Create ``myproject`` folder and enter into it:

.. code-block:: console

    mkdir myproject
    cd myproject

Then create a virtual environment where installed Python packages will be located:

.. code-block:: console

    # This creates venv folder with Python environment for your project
    python3.5 -m venv venv

    # This will activate the environment for your current shell session
    source venv/bin/activate

    # Install Github development version of Websauna
    pip install -e "git+https://github.com/websauna/websauna.git@master#egg=websauna[utils]"

    # Install Websauna from pypi.python.org
    # NOT RELEASED YET
    # Use command below
    # pip install websauna


