# Standard Library
import typing as t

# Pyramid
from pyramid.request import Request
from zope.interface import Interface

# Websauna
from websauna.system.core.interfaces import IRoot
from websauna.system.core.traversal import Resource


def get_human_readable_resource_name(resource: Resource) -> str:
    """Extract human-readable name of the resource for breadcrumbs."""
    # TODO: Add adapter implementation here
    if hasattr(resource, "get_title"):
        return resource.get_title()
    if hasattr(resource, "title"):
        return resource.title
    return resource.__name__


def get_breadcrumbs(context: Resource, request: Request, root_iface: type=None, current_view_name=None, current_view_url=None) -> t.List:
    """Create breadcrumbs path data how to get to this resource from the root.

    Traverse context :class:`Resource` up to the root resource in the reverse order. Fill in data for rendering
    Bootstrap breacrumbs title. Each traversed resource must provide ``get_title()`` method giving a human readable title for the resource.

    :param current_view_name: Optional user visible name of the current view for the bottom most resource.

    :param current_view_url: Full URL to the current view

    :param root_iface: If you want to traverse only subset of elements and stop a certain parent, optional root can be marked with an interface. If not given assume :class:`websauna.system.core.interfaces.IRoot`. Optionally traversing is terminated when reaching ``None`` as the ``__parent__`` pointer.

    :return: List of {url, name, resource} dictionaries
    """
    elems = []
    if not root_iface:
        root_iface = IRoot
    assert issubclass(root_iface, Interface), "Traversing root must be declared by an interface, got {}".format(root_iface)

    # Looks like it is not possible to dig out the matched view from Pyramid request,
    # so we need to explicitly pass it if we want it to appear in URL
    if current_view_name:
        assert current_view_url
        elems.append(dict(url=current_view_url, name=current_view_name))

    while context and not root_iface.providedBy(context):
        if not hasattr(context, "get_title"):
            raise RuntimeError("Breadcrumbs part missing get_title(): {}".format(context))

        elems.append(dict(url=request.resource_url(context), name=get_human_readable_resource_name(context), resource=context))

        if not hasattr(context, "__parent__"):
            raise RuntimeError("Broken traverse lineage on {}, __parent__ missing".format(context))

        if not isinstance(context, Resource):
            raise RuntimeError("Lineage has item not compatible with breadcrums: {}".format(context))

        context = context.__parent__

    # Add the last (root) element
    entry = dict(url=request.resource_url(context), name=get_human_readable_resource_name(context), resource=context)
    elems.append(entry)
    elems.reverse()

    return elems
