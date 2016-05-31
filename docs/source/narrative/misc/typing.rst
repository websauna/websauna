.. _typing:

============
Type hinting
============

.. contents:: :local:

Introduction
============

Websauna supports `Python 3.5 type hints <https://docs.python.org/3/library/typing.html>`_. Type hints add optional static typing information on your variables for tools like code editors and automatic errors checkers. Typing enables more accurate auto completion and background error checking during writing. Static analysis tools like `mypy <http://mypy-lang.org/>`_ can be run against the codebase to catch further errors.

Request type hinting
====================

See :py:class:`websauna.system.http.Request` how to decorate your classes and arguments for type hinting that is only available during run-time.

