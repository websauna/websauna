====
Logs
====

Checking production logs
========================

The most common error you will see is HTTP 500 Internal server error which usually translates to a raised Python exception due to a bug in your code.

To see the traceback for these exceptions in production you can do:

.. code-block:: console

    # ssh into box

    sudo -i -u wsgi

    # Shows last 50 rows of uWSGI log
    tail -n 50 logs/uwsgi.log


See :doc:`post deployment information <./postinfo>` for all available log files.