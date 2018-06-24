# Pyramid
import pyramid.testing
from pyramid.testing import DummyRequest

import pytest

# Websauna
import websauna.system
from websauna.system.core import sitemap
from websauna.system.core.sitemap import ReflectiveSitemapBuilder
from websauna.system.core.sitemap import RouteItem
from websauna.system.core.sitemap import TraverseItem
from websauna.system.http.utils import make_routable_request


@pytest.fixture(scope="module")
def sitemap_app(request, paster_config):
    '''Custom WSGI app with travesal points for sitemap enabled.'''

    class Initializer(websauna.system.DemoInitializer):

        def configure_views(self):
            super(Initializer, self).configure_views()
            from websauna.tests import sitemapsamples
            self.config.add_route('sitemap_test', '/container/*traverse', factory=sitemapsamples.container_factory)
            self.config.scan(sitemapsamples)

    global_config, app_settings = paster_config
    init = Initializer(global_config, app_settings)
    init.run()
    app = init.make_wsgi_app()
    app.init = init
    return app


@pytest.fixture
def sitemap_request(sitemap_app):
    """Create a dummy request object useable for sitemap building tests."""
    return make_routable_request(dbsession=None, registry=sitemap_app.init.config.registry)


@pytest.fixture
def builder(sitemap_request):
    return ReflectiveSitemapBuilder(sitemap_request)


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

    with pyramid.testing.testConfig():
        request = DummyRequest()
        s = sitemap.Sitemap()
        s.add_generator(generator)
        data = s.render(None, request)
        items = list(data["urlset"])
        assert len(items) == 3
        assert items[0].location(request) == "/1"
        assert items[1].location(request) == "/2"
        assert items[2].location(request) == "/3"


def test_reflect_routes(builder):
    """See we can reflect simple routes back to the sitemap."""

    builder.build_routes()
    routes = [i.route_name for i in builder.sitemap.items if isinstance(i, RouteItem)]

    assert "parameter_free_route" in routes
    assert "permissioned_route" not in routes
    assert "post_only_route" not in routes


def test_reflect_traverse(builder):
    """See we can reflect traverse hierarchy back to the sitemap."""
    builder.build_traverse_trees()
    request = builder.request
    urls = [i.location(request) for i in builder.sitemap.items if isinstance(i, TraverseItem)]

    # Admin traversing is protected by view permission
    assert not(any("admin" in u for u in urls))

    # We get default view (empty name) and named view
    assert any(u.endswith("/container/") for u in urls)
    assert any(u.endswith("/container/additional") for u in urls)

    # See we nest correctly
    assert any("/nested/foo/" in u for u in urls)
    assert any("/nested/bar/" in u for u in urls)
    assert any("/nested/bar/additional" in u for u in urls)

    # See we dont' grab permissioned views
    assert not (any("permissioned" in u for u in urls))


def test_reflect_build(builder):
    """Build both routes and traversables."""
    builder.build()


def test_conditions(builder):
    """We can enable/disable items in the sitemap using decorators."""

    builder.build_routes()
    routes = [i.route_name for i in builder.sitemap.items if isinstance(i, RouteItem)]
    assert "conditional_route" in routes
    assert "skipped_route" not in routes

    builder.build_traverse_trees()
    request = builder.request
    urls = [i.location(request) for i in builder.sitemap.items if isinstance(i, TraverseItem)]

    assert any("/container/bar/conditional" in u for u in urls)
    assert not any("/container/bar/skipped_conditional" in u for u in urls)
