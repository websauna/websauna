===================
Developing Websauna
===================

.. contents:: :local:


Install from Github
-------------------

Create a virtualenv and install the latest master from Github using pip.

Running tests
-------------

Unit tests are `PyTest based <http://pytest.org/>`_. They use `Selenium browser automation framework <selenium-python.readthedocs.org/>`_ and  `Splinter simplified element interatcion <https://splinter.readthedocs.org/en/latest/>`_.

First test run
++++++++++++++

Prepare wheel archive which will speed up scaffold tests tremendously::

     bash websauna/tests/create_wheelhouse.bash

Create ``setup-test-secrets.bash`` (git ignored) with following content::

    RANDOM_VALUE="x"
    FACEBOOK_CONSUMER_KEY="x"
    FACEBOOK_CONSUMER_SECRET="x"

    export RANDOM_VALUE
    export FACEBOOK_CONSUMER_KEY
    export FACEBOOK_CONSUMER_SECRET

Enable it in your shell:

    source setup-test-secrets.bash

Running all tests silently using a headless test browser::

    py.test websauna --splinter-webdriver=phantomjs --splinter-make-screenshot-on-failure=false --ini=test.ini

More examples
+++++++++++++

Running a single test case with pdb breakpoint support::

    py.test -s --ini=test.ini --splinter-webdriver=phantomjs -k test_login_inactive

Running functional tests with an alternative browser::

    py.test --splinter-webdriver=firefox websauna/tests/test_frontpage.py --ini=test.ini


