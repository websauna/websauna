===============
Troubleshooting
===============

This chapter contains common issues and how to diagnose them.

.. contents:: :local:

Database connection hangs
-------------------------

Check active transactions::

    SELECT * FROM pg_locks pl LEFT JOIN pg_stat_activity psa ON pl.pid = psa.pid;

-> should be empty for no-activity PostgreSQL instance.

Check if you have stale Python processes (test runners, etc.)::

    ps -af|grep python

Example::

     501 37326 13026   0  5:30PM ??         0:02.80 /Users/mikko/code/trees/venv/bin/python /Applications/PyCharm.app/Contents/helpers/pycharm/pytestrunner.py -p pytest_teamcity /Users/mikko/code/trees/trees/trees/tests -s -k test_create_review --ini test.ini

-> Any test should not be running - what we have here is a buggy PyCharm test runner which does not know when to quit. So let's teach it some habits::

    kill -SIGKILL 37326

More info

* http://www.postgresql.org/docs/9.4/interactive/view-pg-locks.html

Dropping database sessions
--------------------------

In the case you have dangling PSQL sessions and you need to operations these sessions prevent you can force the session drop:

.. code-block:: console

    ws-db-shell conf/staging.ini

And then:

.. code-block:: sql

    SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'TARGET_DB' AND pid <> pg_backend_pid();


Notebook doesn't get context variables
--------------------------------------

If your IPython Notebook (web) fails to start with the default variables filled it is usually due to ``ImportError`` in the variable definitions.

* Log in to your server

* Find the IPython Notebook startup file, usually located like::

    /srv/pyramid/myapp/notebooks/user-1/.ipython/profile_default/startup/startup.py

* Execute ``startup.py`` directly from a Notebook prompt

.. code-block:: pycon

    >>> exec(open("/srv/pyramid/myapp/notebooks/user-1/.ipython/profile_default/startup/startup.py").read())

This should show the actual error which causes the context information failure. Then fix your startup script.


Table 'xxx' is already defined for this MetaData instance during unit tests
---------------------------------------------------------------------------

You see SQLAlchemy error like below during the test run::

    sqlalchemy.exc.InvalidRequestError: Table 'xxx' is already defined for this MetaData instance.  Specify 'extend_existing=True' to redefine options and columns on an existing Table object.

This happens due to earlier error with SQLAlchemy initialization. Scroll up in the logs to see the actual error.


ImportError: No module named websauna.system
--------------------------------------------

Example:

.. code-block:: pycon

    >>> import websauna.system
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ImportError: No module named 'websauna.system'

This is due to clash in different Python namespace systems (setup.py, easy_install, pip).

Solution:

.. code-block:: console

    pip uninstall websauna
    pip uninstall websauna.viewconfig
    pip install websauna  # or pip -e for dev version
    pip install websauna.viewconfig
