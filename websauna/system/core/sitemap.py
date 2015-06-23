"""Sitemap generation helpers.

To include a sitemap for your site

* Configure your site sitemaps in :py:meth:`websauna.system.Initializer.configure_sitemap`. Please note that one site can have several maps.

* You add static items to the sitemap, or you can create a Python generator which generates the sitemap URLs in-fly

Example::

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


"""

import abc


class SitemapItem(abc.ABC):
    """Present an item apperearing in the sitemap.

    Pass information about the sitemap entry for the template.
    """

    def __init__(self, changefreq=None, priority=None, lastmod=None):
        self._changefreq = changefreq
        self._priority = priority
        self._lastmod = lastmod

    @abc.abstractmethod
    def location(self, request):
        """Resolve the full URL of the this item in the sitemap.

        :return: URL as a string
        """
        raise NotImplementedError()

    def changefreq(self, request):
        """Return sitemap changefreq string or None if tag not present."""
        return self._changefreq

    def priority(self, request):
        """Return sitemap priority string or None if priority tag string not present."""
        return self._priority

    def lastmod(self, request):
        """Return sitemap lastmod string or None if tag not present."""
        return self._lastmod


class RouteItem(SitemapItem):
    """Add a static Pyramid URL dispatched route to the sitemap. """

    def __init__(self, route_name, changefreq=None, priority=None, lastmod=None, **kwargs):
        super(RouteItem, self).__init__(changefreq, priority, lastmod)
        self.route_name = route_name
        self.kwargs = kwargs

    def location(self, request):
        return request.route_url(self.route_name, **self.kwargs)


class Sitemap:
    """Sitemap helper."""

    def __init__(self):
        self.items = []
        self.generators = []

    def add_item(self, item):
        assert isinstance(item, SitemapItem)
        self.items.append(item)

    def add_generator(self, generator):
        """
        :param generator: Yields SitemapItem instances
        """
        self.generators.append(generator)

    def urls(self):
        """Return an iterable which goes through all SitemapItem objects in this Sitemap."""
        for item in self.items:
            yield item

        for generator in self.generators:
            yield from generator()

    def render(self, context, request):
        """Render the sitemap.

        :return: dict of information for the templates {urlset: SitemapItem iterator}
        """
        return dict(urlset=self.urls())

