from pyramid.testing import DummyRequest
import pyramid.testing

from websauna.system.core import sitemap


def test_route_items():
    """Routed items appear in the sitemap."""

    with pyramid.testing.testConfig() as config:

        request = DummyRequest()
        config.add_route('bar', '/bar/{id}')

        s = sitemap.Sitemap()
        s.add_item(sitemap.RouteItem("bar", id=1, lastmod="2015-01-01"))
        s.add_item(sitemap.RouteItem("bar", id=2, priority="1.0"))
        s.add_item(sitemap.RouteItem("bar", id=3, changefreq="never"))

        data = s.render(None, request)
        items = list(data["urlset"])
        assert len(items) == 3
        assert items[0].location(request) == "http://example.com/bar/1"
        assert items[0].lastmod(request) == "2015-01-01"

        assert items[1].location(request) == "http://example.com/bar/2"
        assert items[1].priority(request) == "1.0"

        assert items[2].location(request) == "http://example.com/bar/3"
        assert items[2].changefreq(request) == "never"


def test_generator_items():
    """Generated items appear in the sitemap."""

    class FooItem(sitemap.SitemapItem):

        def __init__(self, name):
            super(FooItem, self).__init__()
            self.name = name

        def location(self, request):
            return "/" + str(self.name)

    def generator():
        items = [FooItem(1), FooItem(2), FooItem(3)]
        yield from items

    with pyramid.testing.testConfig() as config:

        request = DummyRequest()
        s = sitemap.Sitemap()
        s.add_generator(generator)

        data = s.render(None, request)

        items = list(data["urlset"])
        assert len(items) == 3
        assert items[0].location(request) == "/1"
        assert items[1].location(request) == "/2"
        assert items[2].location(request) == "/3"
