.. _scaffold:

=========
Scaffolds
=========

There are two different starting points for new Websauna projects. Both are available through :term:`pcreate` command.

websauna_app
------------

A standalone Websauna application

websauna_addon
--------------

A Python package / library which you can reuse across Websauna applications.

Addon guidelines and limitations
================================

Never use :py:class:`websauna.system.model.meta.Base` but always leave models baseless and let the application plug them in with :py:func:`websauna.system.model.utils.attach_model_to_base`.

Maintain independent migration history.

Advanced
========

See :py:mod:`websauna.scaffolds` package.
