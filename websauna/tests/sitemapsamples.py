"""Permission test views."""
# Standard Library
import typing as t

# Pyramid
from pyramid.interfaces import ILocation
from pyramid.response import Response
from pyramid.view import view_config
from zope.interface import implementer

# Websauna
from websauna.system.core.interfaces import IContainer
from websauna.system.core.root import Root
from websauna.system.core.route import simple_route
from websauna.system.core.sitemap import include_in_sitemap
from websauna.system.core.traversal import Resource
from websauna.system.http import Request


class SampleResource(Resource):
    """Leaf resource in tree."""

    def __init__(self, request: Request, name: str):
        super(SampleResource, self).__init__(request)
        self.name = name


@implementer(IContainer)
class SampleContainer(SampleResource):
    """Node resource in tree."""

    def __init__(self, request, name):
        super(SampleContainer, self).__init__(request, name)

    def items(self) -> t.Iterable[t.Tuple[str, ILocation]]:
        # Every container instan
        request = self.request

        def construct_child(child_id, resource: Resource):
            # Set __parent__ pointer
            resource = Resource.make_lineage(self, resource, child_id)
            return child_id, resource

        # Assume this gets populated dynamically from the database
        # when items() is first time called.
        yield construct_child("foo", SampleResource(request, "Foo"))
        yield construct_child("bar", SampleResource(request, "Bar"))

        # First level container has second level nested container
        if self.name == "Container folder":
            yield construct_child("nested", SampleContainer(request, "Nested"))


@view_config(context=SampleResource, name="", route_name="sitemap_test")
def default_sample_view(sample_resource: SampleResource, request: Request):
    return Response()


@view_config(context=SampleResource, name="additional", route_name="sitemap_test")
def additional_sample_view(sample_resource: SampleResource, request: Request):
    return Response()


def traverse_condition(context, request):
    return True


@view_config(context=SampleResource, name="conditional", route_name="sitemap_test")
@include_in_sitemap(condition=traverse_condition)
def conditional_sample_view(sample_resource: SampleResource, request: Request):
    return Response()


def skipped_condition(context, request):
    return False


@view_config(context=SampleResource, name="skipped_conditional", route_name="sitemap_test")
@include_in_sitemap(condition=skipped_condition)
def skipped_conditional(sample_resource: SampleResource, request: Request):
    return Response()


@view_config(context=SampleContainer, name="", route_name="sitemap_test")
def default_container_view(sample_resource: SampleResource, request: Request):
    return Response()


@view_config(context=SampleContainer, name="additional", route_name="sitemap_test")
def additional_container_view(sample_resource: SampleResource, request: Request):
    return Response()


@view_config(context=SampleContainer, name="permissioned", route_name="sitemap_test", permission="edit")
def permissioned_container_view(sample_resource: SampleResource, request: Request):
    return Response()


@simple_route("/parameter_free_route", route_name="parameter_free_route")
def parameter_free_route(request: Request):
    return Response()


@simple_route("/parameterized_route/{param}", route_name="parameterized_route")
def parameterized_route(request: Request):
    return Response()


@simple_route("/permissioned_route", route_name="permissioned_route", permission="edit")
def permissioned_route(request: Request):
    return Response()


@simple_route("/post_only_route", route_name="post_only_route", request_method="POST")
def post_only_route(request: Request):
    return Response()


@simple_route("/included_route", route_name="included_route")
@include_in_sitemap(True)
def included_route(request: Request):
    return Response()


@simple_route("/skipped_route", route_name="skipped_route")
@include_in_sitemap(False)
def skipped_route(request: Request):
    return Response()


def condition(context, request):
    return True


@simple_route("/conditional_route", route_name="conditional_route")
@include_in_sitemap(condition=condition)
def another_skipped_route(request: Request):
    return Response()


def container_factory(request):
    """Set up __parent__ and __name__ pointers required for traversal for container root."""
    container = SampleContainer(request, "Container folder")
    root = Root.root_factory(request)
    return Resource.make_lineage(root, container, "container")
