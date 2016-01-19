==================
Coding conventions
==================

Generic coding conventions
==========================

* PEP-8 with unlimited line length

* ``"use strict"`` JavaScript

No generic exception catch
==========================

Do **not** do the following::

    try:
        pass  # database manipulating code goes here
    except Exception as e:
        # Handle generic exception
        pass

Instead of always use a specific exception subclass when catching.

This would also catch transaction conflict exceptions and prevent :term:`optimistic concurrency control` to work properly.
