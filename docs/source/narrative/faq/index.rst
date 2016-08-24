==========================
Frequently asked questions
==========================

.. contents:: :local:

Preface
=======

Here you can find answers to common questions and criticism.

Python 2 vs. Python 3
=====================

Python 3 is technically superior to Python 2: built-in TSL (HTTPS), hundreds of paper cuts fixed in standard library, nested exceptions, asynchronous input/output and optional type hinting.

`Python 3 has better library supports for maintained projects <https://blogs.msdn.microsoft.com/pythonengineering/2016/03/08/python-3-is-winning/>`_.

All common Linux distributions have switched to Python 3 by default.

There is no point of starting a new project in Python 2 anymore. Websauna aims to support fresh projects started after its initial release.

Template engine
===============

You are free to use your favorite template engine. Plug in your template engine in :py:class:`websauna.system.Initializer.configure_templates`.

The default templates are written in :ref:`Jinja 2 <templates>`. Pyramid supports multiple template engines, so you do not need to rewrite these templates. The engines can be mixed and matched to a certain degree. In fact the underlying form widget library :term:`Deform` uses Chameleon templates internally.

Form framework
==============

Pyramid project has multiple supported form frameworks (:term:`Deform`, WTForms, `ToscaWidgets <http://toscawidgets.org/documentation/tw2.core/index.html>`_. You can easily use your favorite form framework for public facing forms.

The default CRUD, administrative interface and form autogeneration are based on Deform. At the time of writing Websauna, Deform was technically superior choice of available form frameworks. However, Websauna CRUD is abstracted. If you want to use your own form framework for CRUD you can plug it in at :py:meth:`websauna.system.crud.views.FormView.create_form`. Just create your own ``FormView`` based view set for another form framework.

Organizing code
===============

With Websauna, the developer is in the driver's seat.

Websauna comes with a default project :ref:`scaffold` which gives a *suggestive* project layout. This project layout, by all means, is not definitive. If you are a novice it is suggested you stick with this. If you have experience you can bring your own best practices of organizing Python files and page templates.

There are no assumptions about file layout: You are free to organize files any way you wish.

* There are zero global variables

* All behavior can be changed during run time (request object available) or configuration time (configuration object available)

* You are in control of an application :term:`WSGI` entry point

* Entry points usually executes :py:class:`websauna.system.Initializer` which sets up default engine parameters (database connection, where to find template folders, wired models).

* You can override default behavior with subclasses :py:class:`websauna.system.Initializer`. Just override or remove each method you do not wish to use. See :py:meth:`websauna.system.Initializer.run` source code of initialization order and methods.

Amount of dependencies
======================

Websauna has many dependencies at the moment. Expect the number of dependencies going down, as they are being cleaned up and unnecessary functionality being culled off.

For example, some of functionality of minor dependencies can be moved to Websauna core. Some of them can be made optional (IPython).

UUIDs or running counter ids
============================

:ref:`For security reasons it is suggested to use non-guessable ids (UUIDs) <uuid-security>`. Websauna embraces security best practices and thus suggests you to stick with this. :ref:`You can still use old fashioned running counter ids <running-counter-id>`.

CRUD supports both behaviors out of the box (see :py:mod:`websauna.system.crud.urlmapper`).

So many things
==============

Websauna integrates existing, well known libraries and provides polished solution based on them. The amount of code in Websauna itself is kept minimal; patches are sent to upstream libraries. New features are planned to rolled out as a separate libraries for maximum reusability even though they would start their life inside Websauna core.

The minimal viable features set for Websauna is a website where you can login and sign up out of the box, have easy administrative  access to data, all this in security critical environment.

Future
======

Websauna is used in professional projects which are expected to last several years. There is a community building around it, albeit currently it is still in its infancy.

