=============
Running tests
=============

Preparing tests
===============

Tests usually require a database access. Tests use the database named in :ref:`test.ini`- usually format of ``myapp_test``.

This :term:`PostgreSQL` database must be created before the test run. It is not dropped, but is cleaned, from the content between individual tests.

Create test database on OSX
---------------------------

Run:

.. code-block:: console

    createdb myapp_dev

Create test database on Ubuntu
------------------------------

Run:

.. code-block:: console

    sudo -u postgres createdb myapp_dev

Running tests
=============

Use `py.test command <http://pytest.org/latest/usage.html>`_. ``py.test`` should be available in ``bin`` of your virtual environment if you installed your Websauna application package with ``pip install -e ".[test]"``.

Example to run all tests for ``myapp`` package. Run the following in the package root folder:

.. code-block:: console

    py.test myapp --ini conf/test.ini


Example to run a single test using ``-k`` regex match of test names:

.. code-block:: console

    py.test myapp --ini conf/test.ini -k test_login

Pytest buffers stdout by default and you will miss all print and log statements. If you wish to see these use ``-s`` switch:

.. code-block:: console

    py.test myapp --ini conf/test.ini -s

If you are running multiple tests and want to abort after first failing test use ``-x``:

.. code-block:: console

    py.test myapp --ini conf/test.ini -x

Splinter settings
=================

Websauna uses :term:`Splinter` and :term:`pytest-splinter` packages for browser based testing. Besides normal *pytest-splinter* command line based configuration, Websauna supports INI based configuration. For more information see :py:func:`websauna.tests.conftest.browser`.

