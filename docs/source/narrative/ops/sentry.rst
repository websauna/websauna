====================
Sentry error logging
====================

Introduction
============

`Sentry <http://sentry.readthedocs.org/>`_ is a popular open source error logging server for Python application.

How to
======

Install pyramid_raven::

    pip install pyramid_raven

Add in your ``production.ini``::

    pyramid.includes =
        pyramid_raven
        ...


    # pyramid_raven.swallow_parse_errors = False
    raven.dsn = https://x:y@sentry.example.com


