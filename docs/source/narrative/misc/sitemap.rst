.. _sitemap:

=======
Sitemap
=======

.. contents:: :local:

Introduction
============

Sitemap is a Google defined XML file format to include your site content in search engine indexes. Websauna supports automatic and manual sitemap generations.

More information

* https://support.google.com/webmasters/answer/156184?hl=en

Automatic sitemap generation
============================

Automatic sitemap generation inspects your site URL configuration from Pyramid router. It enumerates all routes and recurses into :ref:`traversable <traversal>` hierarchies. All public views that are accesible through HTTP GET are added to the sitemap.

Automatic sitemap generation uses :py:class:`websauna.system.core.interfaces.IContainer` protocol to determine whether traversable resources have children or not.

Automatic sitemap generation is one of powerful use cases of traversal based routing.

.. note ::

    Automatic sitemap generation doesn't work with parametrized public urls like ``/my_view/{object-id}``. Thus, it is recommended to :ref:`traversal` based routing if you have any container like URLs.


For more information see

* :py:class:`websauna.system.core.sitemap.ReflectiveSitemapBuilder`.

* :py:mod:`websauna.tests.sitemapsamples` and :py:mod:`websauna.tests.test_sitemap`

Manual sitemap generation
=========================

To include a sitemap for your site

* Configure your site sitemaps in :py:meth:`websauna.system.Initializer.configure_sitemap`. Please note that one site can have several maps.

* You add static items to the sitemap, or you can create a Python generator which generates the sitemap URLs in-fly

* For more information see :py:mod:`websauna.system.core.sitemap``.

Example:

.. code-block:: python

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
