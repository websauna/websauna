===================
Developing Websauna
===================

.. contents:: :local:


Prerequisites
-------------

In order to develop Websauna, the following requirements need to be installed on your system:

    * GCC, make, and similar
    * Python 3.5 with development headers
    * virtualenv
    * pip
    * git
    * Google Chrome
    * :term:`chromedriver`
    * PostgreSQL
    * Redis

Ubuntu
++++++

.. code-block:: console

    apt-get install build-essential python-dev python-virtualenv python-pip git redis postgresql


Install from GitHub
-------------------

Considering a local work folder name Websauna, clone websauna and websauna.ansible repositories from the GitHub:

.. code-block:: console

    cd Websauna
    git clone git@github.com:websauna/websauna.ansible.git
    git clone git@github.com:websauna/websauna.git

Now, create a virtualenv and install websauna into it.

.. code-block:: console

    cd websauna
    python3.5 -m venv venv
    source venv/bin/activate
    pip install -e ".[test, dev, celery, utils, notebook]"


Building docs
-------------

To generate Sphinx docs locally, run the following:

.. code-block:: console

    cd docs
    make all


Documentation will be generated inside the build/html folder.

.. note:: To publish the documentation use ``make world`` instead.


Running tests
-------------

Unit tests are `PyTest based <http://pytest.org/>`_. They use `Selenium browser automation framework
<http://selenium-python.readthedocs.org/>`_ and `Splinter simplified element interaction
<https://splinter.readthedocs.org/en/latest/>`_.


First test run
++++++++++++++

Create ``setup-test-secrets.bash`` (git ignored) with following content:

.. code-block:: bash

    RANDOM_VALUE="x"
    FACEBOOK_CONSUMER_KEY="x"
    FACEBOOK_CONSUMER_SECRET="x"
    FACEBOOK_USER="x"
    FACEBOOK_PASSWORD="x"

    export RANDOM_VALUE
    export FACEBOOK_CONSUMER_KEY
    export FACEBOOK_CONSUMER_SECRET
    export FACEBOOK_USER
    export FACEBOOK_PASSWORD


Enable it in your shell:

.. code-block:: console

     source setup-test-secrets.bash

Tests assume that you have Redis running, make sure you do:

.. code-block:: console

    redis-server

Running all tests silently using a headless test browser:

.. code-block:: console

    py.test --ini=websauna/conf/test.ini --splinter-webdriver=chrome --splinter-headless=true


.. note:: Pytest sensible defaults are set on the *setup.cfg* file, on the top level of websauna repository.


Tox
---

:term:`Tox` is used to run tests against multiple versions of Python.

To run tests locally using tox:

.. code-block:: console

    tox -- --ini=websauna/conf/test.ini

More examples
-------------

Run tests using Tox. Here is a Tox run using Python 3.5 and Chrome:

.. code-block:: console

     tox -e py35 -- --ini=websauna/conf/test.ini -x --splinter-webdriver=chrome

Running a single test case with pdb breakpoint support:

.. code-block:: console

    py.test -s --ini=test.ini --splinter-webdriver=phantomjs -k test_login_inactive

Running functional tests with an alternative browser:

.. code-block:: console

    py.test --ini=websauna/conf/test.ini --splinter-webdriver=firefox websauna/tests/test_frontpage.py
