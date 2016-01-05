===================
Developing Websauna
===================

.. contents:: :local:


Running tests
--------------

Unit tests are `PyTest based <http://pytest.org/>`_. They use `Selenium browser automation framework <selenium-python.readthedocs.org/>`_ and  `Splinter simplified element interatcion <https://splinter.readthedocs.org/en/latest/>`_.

Examples for running tests
++++++++++++++++++++++++++

Running all tests silently using a headless test browser::

    py.test websauna --splinter-webdriver=phantomjs --splinter-make-screenshot-on-failure=false --ini=test.ini

Running a single test case with pdb breakpoint support::

    py.test -s --ini=test.ini --splinter-webdriver=phantomjs -k test_login_inactive

Running functional tests with an alternative browser::

    py.test --splinter-webdriver=firefox websauna/tests/test_frontpage.py --ini=test.ini

More info

* http://pytest.org/latest/usage.html

Writing tests
----------------

* `Spinter WebDriver convenience API <https://github.com/cobrateam/splinter/blob/master/splinter/driver/webdriver/__init__.py>`_

