=======
Sitemap
=======

.. contents:: :local:

Introduction
============

Sitemap is a Google defined XML file format to include your site content in search engine indexes. Websauna supports automatic and manual sitemap generations. Sitemaps are one of the most crucial search engine optimizations.

Usually the sitemap is accessible at ``/sitemap.xml`` path on your site. Then you submit this path to `Google Webmasters tool <https://google.com/webmasters>`_.

More information

* https://support.google.com/webmasters/answer/156184?hl=en

_ ..automatic-sitemap:

Automatic sitemap generation
============================

Automatic sitemap generation inspects your site URL configuration from Pyramid router. It enumerates all routes and recurses into :ref:`traversable <traversal>` hierarchies. All public views that are accessible through HTTP GET are added to the sitemap.

Automatic sitemap generation uses :py:class:`websauna.system.core.interfaces.IContainer` protocol to recurse into the children of traversable resources.

Automatic sitemap generation is one of more powerful use cases of traversal based routing.

.. note::

    Automatic sitemap generation doesn't work with parametrized public urls like ``/my_view/{object-id}``. Thus, it is recommended to :ref:`Traversal <traversal>` based routing if you have any container like URLs. If you use parametrized URL dispatching and you want to these routes to be included in the sitemap, see Manual sitemap generation below.

Set up the sitemap handler in :py:meth:`websauna.system.Initializer.configure_sitemap`. Example:

.. code-block:: python

    from pyramid.interfaces import IRequest

    class Initializer(websauna.system.Initializer):

        def configure_sitemap(self):
            from websauna.system.core.sitemap import ReflectiveSitemapBuilder
            self.config.add_route("sitemap", "/sitemap.xml")
            self.config.add_view(ReflectiveSitemapBuilder.render, route_name="sitemap", renderer="core/sitemap.xml")

Test that your sitemap opens at ``/sitemap.xml`` on your :ref:`local development server <devserver>`. Potentially issues are caused by routes and traversing endpoints that do not have proper permissions set up and do not behave well with anonymous GET requests.

You can customize automatic sitemap generation by subclassing :py:class:`websauna.system.core.sitemap.ReflectiveSitemapBuilder` and overriding various parts of it.

For more information see

* :py:class:`websauna.system.core.sitemap.ReflectiveSitemapBuilder`.

* :py:mod:`websauna.tests.sitemapsamples` and :py:mod:`websauna.tests.test_sitemap`

Exclusion of views
------------------

Sometimes you don't want automatically discovered view to appear in the sitemap. Google crawler penalizes crawling your site if you include non-functional, non-GET, views in the sitemap. Example cases you might want to exclude from the sitemap include

* POST only views

* AJAX views

Use :py:func:`websauna.system.core.sitemap.include_in_sitemap` to either hardcode or have dynamic conditions (context, request) to determine if views should appear in the automatically generated sitemap.

Manual sitemap generation
=========================

To include a sitemap for your site

* Configure your site sitemaps in :py:meth:`websauna.system.Initializer.configure_sitemap`. Please note that one site can have several maps.

* You add static items to the sitemap, or you can create a Python generator which generates the sitemap URLs in-fly

* For more information see :py:mod:`websauna.system.core.sitemap`.

Example:

.. code-block:: python

   class Initializer(websauna.system.Initializer):

       def configure_sitemap(self, settings):
            # Configure sitemap generation for your site.

            from websauna.system.core import sitemap

            map = sitemap.Sitemap()

            # Add sitemap itself to /sitemap.xml path
            self.config.add_route("sitemap", "/sitemap.xml")
            self.config.add_view(map.render, route_name="sitemap", renderer="core/sitemap.xml")

            # Add static items to the sitemap by their route_name
            map.add_item(sitemap.RouteItem("home"))
            map.add_item(sitemap.RouteItem("info"))

            # Generate a sitemap entry for each product in the product descriptions.
            # Each of these have static route_url()
            def generate_product_pages():
                for name, description in models.PRODUCT_INFO.items():
                    if "page" in description:
                        yield sitemap.RouteItem(description["page"])

            map.add_generator(generate_product_pages)
