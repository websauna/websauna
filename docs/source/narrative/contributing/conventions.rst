==================
Coding conventions
==================

Generic coding conventions
==========================

* PEP-8 without hard line lengths

* ``"use strict"`` JavaScript

Line length
-----------

The code line length is the varying window width of the author, soft wrapped.

All prose, regardless if it is in source code or not, should follow the normal text editing practices: a hard line break terminates a paragraph - or two line breaks for where it applies (restructured text). This namely applies to comments, doctstrings and other text strings.

For the sake of clarity, too long code lines should be broken down. This should happen through the means of refactoring the code to be more sensible instead of hard terminating lines with ``\`` operator or similar. For example, split your code to several Python statements and helper functions.

Generally, keep your lines under 132 characters. `Consider this guidelining <https://www.youtube.com/watch?v=b6kgS_AwuH0>`_ as the line length is still what the width of editor window of the author happens to be on that day, as it might be narrower in two columns mode or wider in full screen mode. And this number was only chosen because of the complaints of an anynomous contributor saying his GitHub text viewer cannot display lines longer than this particular number without a horizontal scroll bar. For this blasphemy I immediately called to GitHub as a paying customer and complained why they chose this number and not some nice number like 142 what it is in my web browser.

Text processors have been able to wrap text lines sensible since RAM limitations allowed it first time in 1979. It's sad that computer programmers, who write these applications, often do not have this ability in their own tools. Every programmer agrees that it should be the job of a machine to wrap lines in intelligent manner in the context they are viewed. Let's push for a change, so that tooling gets better and we can get rid of line length debate once and for all.

Import order
------------

Imports should be ordered by their origin. Names should be imported in this order:

    #. Future (__future__)
    #. Python standard library
    #. Pyramid imports
    #. SQLAlchemy imports
    #. Third party packages
    #. Websauna imports
    #. Other modules from the current package

.. warning:: Do not import all the names from a package (in other words, never use from package import \*); import just the ones that are needed. Single-line imports apply here as well: each name from the other package should be imported on its own line.

No mutable objects as default arguments
=======================================

Remember that since Python only parses the default argument for a function/method just once, they cannot be safely used as default arguments.

Do **not** do this:

.. code-block:: python

    def somefunc(default={}):
        if default.get(...):
            # do something


.Either of these is fine:

.. code-block:: python

    def somefunc(default=None):
        default = default or {}



.. code-block:: python

    def somefunc(default=None):
        if default is None:
            default = {}


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
