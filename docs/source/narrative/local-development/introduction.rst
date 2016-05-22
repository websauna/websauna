============
Introduction
============

Websauna uses local development workflow.

* Developers install and run Python and Websauna on their local computer (see :ref:`tutorial <gettingstarted>`)

* The development happens against a :ref:`local development web server <devserver>` that automatically reloads edited code and there is no need to manually start and stop a server

* The local development web server has development, diagnose and debugging extras like :term:`pyramid_debugtoolbar`, :ref:`outgoing email echo to console <mail>`

* The local development web server refuses to start if your :ref:`models` do not match the database (you have unrun migrations)

