================================
Developing pyramid_web20.core
================================

.. contents:: :local:


Running tests
--------------

Unit tests are `PyTest based <http://pytest.org/>`_.

Examples for running tests
+++++++++++++++++++++++++++

Running all tests::

    py.test pyramid_web20

Running a single test case with ipdb breakpoint support::

    py.test –s pyramid_web20/core/tests/test_conflictresolver.py

Running functional tests with an alternative browser (Firefox is default)::

    py.test --splinter-webdriver=phantomjs pyramid_web20/tests/test_frontpage.py

Running a single test::

    py.test -k "BitcoindTestCase.test_send_internal" pyramid_web20

Running a single test with verbose Python logging output to stdout (useful for pinning down *why* the test fails)::

    VERBOSE_TEST=1 py.test -k "BitcoindTestCase.test_send_internal" pyramid_web20

Running tests for continuous integration service (15 minute timeout) and skipping slow tests where transactions are routed through cryptocurrency network (full BTC send/receive test, etc.)::

    CI=true py.test pyramid_web20

Running unittests using vanilla Python 3 unittest::

    python -m unittest discover

(This ignores all skipping hints)

More info

* http://pytest.org/latest/usage.html
