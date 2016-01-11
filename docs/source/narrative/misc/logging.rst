=======
Logging
=======

Websauna uses Python's :py:mod:`logging` subsystem.

* Logging configured is INI based configuration file

* You can set logging level for each module individually

Logging from your code
======================

Use the standard module-level ``logger`` pattern::

    import logging

    # ... Imports go here ...

    logger = logging.getLogger(__name__

    # ... later in your code ...


    def my_func(a, b):
        logger.debug("Entering my_func, a: %s, b: %s", a, b)

.. note ::

    You need to pass the raw objects to the logger message function instead of an interpolated string. Some specialized loggers like :term:`Sentry` will use this information.

.. note ::

    Loggers still take Python old style %s string formatting instead of {}: This is `a well known issue <http://stackoverflow.com/questions/13131400/logging-variable-data-with-new-format-string>`_ in Python.

Logging setup
=============

Command line applications have their special logging setup. See :py:func:`websauna.system.devop.cmdline.setup_logging`.

More info
=========

`Python Logging HOWTO <https://docs.python.org/3.5/howto/logging.html>`_.