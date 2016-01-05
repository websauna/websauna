===============
Troubleshooting
===============

This chapter contains common issues and how to diagnose them.

..

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