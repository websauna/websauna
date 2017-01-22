============
Introduction
============

Websauna uses a local development workflow.

* Developers install and run Python and Websauna on their local computer (see :ref:`tutorial <gettingstarted>`)

* The development happens with a :ref:`local development web server <devserver>` that automatically reloads edited code and there is no need to manually start and stop a server

* The local development web server has development, diagnostic and debugging extras enabled like :term:`pyramid_debugtoolbar`, :ref:`outgoing email echo to console <mail>`

* The local development web server refuses to start if your :ref:`models` do not match the current database layout (you have to rerun migrations)

