=========================
HTTP request and response
=========================

Websauna uses Pyramid's `request processing <http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/router.html>`_.

Request and response
--------------------

The incoming HTTP request is an instance of :py:class:`websauna.system.http.Request`.

When your view function returns

* If the return value is instance of :py:class:`pyramid.response.Response` it is processed as is

* If the return value is a dictionary, as usually it is to pass template context variables to template rendering, a corresponding :term:`renderer` is invoked to turn the context to a response. The ``renderer`` argument to view configuration is a template name. The template engine loads this template and passes the view return value to it as template context.

Routing
-------

Routing to a corresponding view function or class is done by Pyramid's routing mechanism (`URL dispatch <http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/urldispatch.html>`, `traversal <http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/traversal.html>`_). You set up this in :term:`Initializer`.

Related methods include

* :py:meth:`pyramid.configurator.Configurator.add_view`

* :py:meth:`pyramid.configurator.Configurator.add_route`

* :py:func:`websauna.system.core.route.simple_route`

Tweens
------

You can install :doc:`tweens <./tweens>` (be'tween) to sit between the routing and view processing to have extensible mechanism which needs to process every request or response.


