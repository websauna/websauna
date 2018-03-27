"""Sitemap generation helpers."""
# Standard Library
import abc
import typing as t

# Pyramid
from pyramid.config import Configurator
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import ITraverser
from pyramid.registry import Introspectable
from pyramid.router import Router
from pyramid.scripts.proutes import _get_pattern
from pyramid.security import Everyone
from pyramid.static import static_view
from pyramid.traversal import ResourceTreeTraverser
from pyramid.urldispatch import Route

# Websauna
from websauna.system.core.interfaces import IContainer
from websauna.system.core.traversal import Resource
from websauna.system.http import Request
from websauna.system.http.utils import make_routable_request


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


class TraverseItem(SitemapItem):
    """Add a travered resource view to the sitemap."""

    def __init__(self, context: Resource, view_name, changefreq=None, priority=None, lastmod=None, **kwargs):
        super(TraverseItem, self).__init__(changefreq, priority, lastmod)
        self.context = context
        self.view_name = view_name

    def location(self, request):
        return request.resource_url(self.context, self.view_name)


class Sitemap:
    """Sitemap helper.
    See :ref:`Sitemap <sitemap>`.

    .. _sitemap:
    """

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
        request.response.content_type = "application/xml"
        return dict(urlset=self.urls())


class ReflectiveSitemapBuilder:
    """Scan all registered routes and traversable resources and build sitemap from them automatically.

    This will read route configuration and build sitemap for

    * All routes without parameter

    * All traversable endpoints that implement :py:class:`websauna.system.core.interfaces.IContainer` protocol

    * GET accessible views

    This method might not yet work for more advanced view configuration use cases. Check :py:mod:`websauna.tests.sitemapsamples` for covered use cases.

    See :ref:`Sitemap <sitemap>` for examples.
    """

    def __init__(self, request: Request):
        self.request = request
        self.sitemap = Sitemap()

    def get_mapper(self):
        config = Configurator(registry=self.request.registry)
        return config.get_routes_mapper()

    def is_parameter_free_route(self, route_spec: str):
        # no {param}, no traverse/*
        return ("{" not in route_spec) and ("*" not in route_spec)

    def is_traversable_sitemap_route(self, route: Route):
        """Is this route such that it 1) is traversable 2) can be added to sitemap"""

        if not route.factory:
            # /notebook/*remainder
            # static view
            return False

        return "*" in route.pattern

    def is_get_requestable(self, view_data: dict):

        if not view_data.get("request_methods"):
            return True

        return "GET" in view_data["request_methods"]

    def is_anonymous(self, view_data: dict):

        # TODO: This does not handle the case where
        # multiple derivates are stacked
        derived = view_data.get("derived_callable")
        if derived:
            if getattr(derived, "__permission__", None):
                return False

        return True

    def is_static(self, view_data: dict):
        return isinstance(view_data.get("callable"), static_view)

    def is_public_get_view(self, view_data: dict):
        """Check if view can be publicly accessed

        :param view_data: Introspected view data as dict
        """

        if not self.is_get_requestable(view_data):
            return False

        if not self.is_anonymous(view_data):
            return False

        return True

    def is_included(self, view_data: dict, context: t.Optional[Resource], request: Request):
        """Check if sitemap conditions allow to include this item."""

        callable = view_data.get("callable")
        if callable is None:
            # This is route like admin_home without callable, only traversing nesting
            return True

        # TODO: Not sure if we need to peek through callable decorator stack
        sitemap_data = getattr(callable, "_sitemap_data", None)
        if sitemap_data is None:
            return True

        # Hardcoded condition
        included = sitemap_data.get("include", None)
        if included is not None:
            return included

        condition = sitemap_data["condition"]
        return condition(context, request)

    def is_good_route_item(self, name, pattern, view_data):
        """Check conditions if routed view can be added in the sitemap."""

        # view_data.keys()
        # dict_keys(['mapper', 'header', 'check_csrf', 'predicates', 'containment', 'attr', 'route_name', 'request_methods', 'order', 'xhr', 'path_info', 'phash', 'callable', 'decorator', 'name', 'request_param', 'context', 'require_csrf', 'derived_callable', 'accept', 'http_cache', 'match_param'])

        if not self.is_parameter_free_route(pattern):
            return False

        if not self.is_public_get_view(view_data):
            return False

        if not self.is_included(view_data, None, self.request):
            return False

        return True

    def has_public_view_acl(self, context: Resource):
        """Check if ACL for the resource is publicly viewable.

        View permission must be either missing or pyramid.security.Everyone.
        """
        policy = self.request.registry.queryUtility(IAuthorizationPolicy)

        # view permission is set on Root object or overridden in resource hierarchy __ACL__
        principals = policy.principals_allowed_by_permission(context, "view")
        return Everyone in principals

    def add_route_item(self, name, pattern, view_data):
        """Add one route item to the table.

        Override for custom sitemap parameters (changefreq, etc.).
        """
        self.sitemap.add_item(RouteItem(name))

    def add_traverse_item(self, context: Resource, view_name: str):
        """Add one traverse item to the table.

        Override for custom sitemap parameters (changefreq, etc.).
        """
        self.sitemap.add_item(TraverseItem(context, view_name))

    def build_routes(self):
        """Build all routes without parameters and permissions."""
        mapper = self.get_mapper()
        routes = mapper.get_routes(include_static=False)

        for route in routes:
            data = _get_route_data(route, self.request.registry)
            for name, pattern, view_data in data:

                if self.is_good_route_item(name, pattern, view_data):
                    self.add_route_item(name, pattern, view_data)

    def enumerate_available_views(self, route: Route, context: Resource) -> t.Iterable[Introspectable]:
        """Get list of available views for a given resource."""
        introspector = self.request.registry.introspector
        views = introspector.get_category("views")

        # We can have multiple views with the same name for the same resource because of inheritance.
        available_views = {}

        for v in views:
            spectable = v["introspectable"]  # pyramid.registry.Introspectable

            # See discrim_func() in add_view()
            cat, intr_context_cls, name, route_name, phash = spectable.discriminator

            if not intr_context_cls:
                continue

            if route_name != route.name:
                # On a different route
                continue

            if isinstance(context, intr_context_cls):
                # TODO: Assumes that the later defined views have more accurate context scope.
                # Not sure if this holds true all the time.
                available_views[name] = v["introspectable"]

        return available_views.values()

    def get_traverse_endpoint_context(self, router: Router, route: Route) -> Resource:
        """Get root object for a traversable route.

        E.g. resolve /container/* to a SampleContainer context.
        """

        # chop off last part /container/*traverse'
        start_path = "/".join(route.pattern.split("/")[0:-2]) + "/"

        # create a new request to traverse based on detected route pattern
        # dbsession must be passed here to prevent creating new dbsession
        sample_request = make_routable_request(
            dbsession=self.request.dbsession,
            registry=self.request.registry,
            path=start_path
        )

        root = route.factory(sample_request)

        traverser = self.request.registry.queryAdapter(root, ITraverser)
        # We are about to traverse and find a context
        if traverser is None:
            traverser = ResourceTreeTraverser(root)

        # {'virtual_root': <websauna.tests.sitemapsamples.SampleContainer object at 0x104656f98>, 'traversed': (), 'root': <websauna.tests.sitemapsamples.SampleContainer object at 0x104656f98>, 'virtual_root_path': (), 'view_name': 'container', 'subpath': (), 'context': <websauna.tests.sitemapsamples.SampleContainer object at 0x104656f98>}
        tdict = traverser(sample_request)
        context = tdict["context"]
        return context

    def recurse_traversable(self, router: Router, route: Route, context: Resource):
        """Walk through traversable hierarchy.

        For each context iterate available views and add to sitemap.
        """

        if not self.has_public_view_acl(context):
            # This resource limits view permission to subgroup and is not public. E.g. /admin/*
            return

        # Add all views for this leaf
        for view_data in self.enumerate_available_views(route, context):
            if self.is_public_get_view(view_data) and self.is_included(view_data, context, self.request):
                self.add_traverse_item(context, view_data["name"])

        # Recurse to children
        if IContainer.providedBy(context):
            for name, child in context.items():
                self.recurse_traversable(router, route, child)

    def build_traverse_trees(self):
        """Build all traversed hierarchies."""
        mapper = self.get_mapper()
        router = Router(self.request.registry)

        routes = mapper.get_routes(include_static=False)

        for route in routes:
            if not self.is_traversable_sitemap_route(route):
                continue

            root_context = self.get_traverse_endpoint_context(router, route)
            self.recurse_traversable(router, route, root_context)

    def build(self):
        """Iterate through all public routes and traversable items and add them to the sitemap."""
        self.build_routes()
        self.build_traverse_trees()

    def get_sitemap(self) -> Sitemap:
        """Get ready sitemap after build."""
        return self.sitemap

    @classmethod
    def render(cls, context, request):
        """Render the sitemap.

        TODO: I don't like that Sitemap.render is little bit different from this one.

        :return: dict of information for the templates {urlset: SitemapItem iterator}
        """
        reflective_builder = cls(request)
        reflective_builder.build()
        map = reflective_builder.get_sitemap()
        return map.render(context, request)


def _get_route_data(route, registry):
    """Iterate all non static views for a route.

    :param route: Route introspection data
    :param registry:
    :yield: (route name, route pattern, view introspection data) tuples
    """

    pattern = _get_pattern(route)

    request_iface = registry.queryUtility(
        IRouteRequest,
        name=route.name
    )

    route_intr = registry.introspector.get(
        'routes', route.name
    )

    if request_iface is None:
        return

    if route_intr.get('static', False) is True:
        return

    view_intr = registry.introspector.related(route_intr)

    if view_intr:
        for view in view_intr:
            yield route.name, pattern, view


def include_in_sitemap(include: t.Optional[bool]=None, condition: t.Optional[t.Callable]=None):
    """A function decorator to determine if a view should be included in the automatically generated sitemap.

    You need to give either ``include`` argument or ``condition``. If this view decorator is not present the view is always included.

    Example of hardcoded condition for an URL dispatch view:

    .. code-block:: python

        from websauna.system.core.sitemap import include_in_sitemap
        from websauna.system.core.route import simple_route


        @simple_route("/skipped_route", route_name="skipped_route")
        @include_in_sitemap(False)
        def skipped_route(request: Request):
            return Response()

    Example of dynamic condition for a traverse view:

    .. code-block:: python

        from websauna.system.core.sitemap import include_in_sitemap
        from pyramid.view import view_config


        def skipped_condition(context, request):
            return False


        @view_config(context=SampleResource, name="skipped_conditional", route_name="sitemap_test")
        @include_in_sitemap(condition=skipped_condition)
        def skipped_conditional(sample_resource: SampleResource, request: Request):
            return Response()

    More complex example where you dynamically look up from the database if the content exist and then have the item in the sitemap:

    .. code-block:: python

        # We reuse this helper function in sitemap condition and actual view
        def get_insight_content(asset_resource):
            asset = asset_resource.asset
            content = asset.asset_content.filter_by(content_type=AssetContentType.insight).one_or_none()
            return content


        @view_config(context=AssetDescription, route_name="network", name="insight", renderer="network/asset_insight.html")
        @include_in_sitemap(lambda c, r: get_insight_content(c) is not None)
        def insight(asset_resource: AssetDescription, request: Request):
            breadcrumbs = get_breadcrumbs(asset_resource, request, current_view_name="Asset insight", current_view_url=request.resource_url(asset_resource, "insight"))
            content = get_insight_content(asset_resource)

            if content:
                body = markdown.markdown(content.text)
            else:
                body = "This research has not yet been published"

            return locals()

    :param include: Either ``True`` or ``False``

    :param condition: callback function (context, request) to called to every item. Traversable views get both route and request, URL dispatch views get only request. Return true if the item should be included in the sitemap.
    """

    assert (include is not None) or (condition is not None), "You need to give either include or condition argument"

    def _outer(view_func):
        # Store data directly on a view function
        view_func._sitemap_data = dict(include=include, condition=condition)
        return view_func

    return _outer
