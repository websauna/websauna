===================
Developing Websauna
===================

.. contents:: :local:


Prerequisites
-------------

* GCC, make, and similar (``apt-get install build-essential``)
* Python 3.5 with development headers (``apt-get install python-dev``)
* virtualenv (``apt-get install python-virtualenv``)
* pip (``apt-get install python-pip``)
* git (``apt-get install git``)
* PhantomJS headless browser (``apt-get install phantomjs``)
* Redis (``apt-get install redis``)


Install from Github
-------------------

Create a virtualenv and install the latest master from Github using pip.

.. code-block:: bash

    ~$ cd <your_work_folder>
    work$ git clone git@github.com:websauna/websauna.ansible.git
    work$ git clone git@github.com:websauna/websauna.git
    work$ cd websauna
    websauna$ virtualenv -p python3.5 venv
    websauna$ source venv/bin/activate
    (venv) websauna$ pip install -e ".[test, dev, celery]"


Building docs
-------------

To generate Sphinx docs locally, run the following:

.. code-block:: bash

    (venv) websauna$ cd docs
    (venv) docs$ make world


Running tests
-------------

Unit tests are `PyTest based <http://pytest.org/>`_. They use `Selenium browser automation framework
<http://selenium-python.readthedocs.org/>`_ and `Splinter simplified element interatcion
<https://splinter.readthedocs.org/en/latest/>`_.


First test run
++++++++++++++

Prepare wheel archive which will speed up scaffold tests tremendously:

.. code-block:: bash

    (venv) websauna$ bash websauna/tests/create_wheelhouse.bash

Create ``setup-test-secrets.bash`` (git ignored) with following content::

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

.. code-block:: bash

     (venv) websauna$ source setup-test-secrets.bash

Tests assume that you have Redis running, make sure you do:

.. code-block:: bash

    (venv) websauna$ redis-server

Running all tests silently using a headless test browser::

    (venv) websauna$ py.test websauna --splinter-webdriver=phantomjs --splinter-make-screenshot-on-failure=false --ini=test.ini


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

    py.test --splinter-webdriver=firefox websauna/tests/test_frontpage.py --ini=test.ini


