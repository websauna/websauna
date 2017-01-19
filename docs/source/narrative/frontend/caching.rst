=======
Caching
=======

.. contents:: :local:

Introduction
============

Caching allows serve content faster by storing pre-generated content in memory instead of generating content fully from the scratch for every request.


Setting HTTP response caching headers
=====================================

Caching in view decorators
--------------------------

You can pass ``http_cache`` (seconds) to both py:func:`websauna.system.core.route.simple_route` and :py:func:`pyramid.view.view_config` decorators to set caching time for the resulting HTTP response in the front end web server. The front end web server must be properly tuned for caching (Cloudflare, Apache mod_cache, Nginx proxy_cache, Varnish).

You need to set ``public`` option to generate ``Cache-control: public`` header, or otherwise pages are not cached for HTTPS connections.

Example:

.. code-block:: python

    from websauna.system.core.route import simple_route

    @simple_route("/calendar-widget",
        route_name="calendar_widget",
        renderer="partners/calendar_widget.html",
        http_cache=(3600, {"public": True}))
    def calendar_widget(request: Request)
        # ...

More information

* :py:meth:`pyramid.config.Configurator.add_view`

Caching manually generated HTTP responses
-----------------------------------------

.. code-block:: python

    from pyramid.response import Response

    @simple_route("/partner-rss-feed", route_name="partner_rss_feed")
    def partner_rss_feed(request: Request):
        """Media partners ICO RSS feed."""
        items = get_partner_rss_feed_items(request.dbsession)
        feed = generate_rss(request, items)

        # Generate RSS feed response
        resp = Response(body=feed.rss(), content_type="application/rss+xml")

        # Ten minutes
        cache_timeout = 10*60

        # Set cache headers for downstream web server (Cloudflare)
        # so that we don't hit the back end for every request
        resp.cache_expires = cache_timeout
        resp.cache_control.public = True  # Needed to cache HTTPS content

        return resp