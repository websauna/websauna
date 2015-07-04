from abc import abstractmethod


class Resource:
    """Traversable resource part.

    Wraps underlying object into a traverse path.
    """

    def __init__(self):

        #: Pointer to the parent object in traverse hierarchy. This is none until make_lineage is called.
        self.__parent__ = None

        #: The id of this resource as its appear in URL and traversing path
        self.__name__ = None

    def get_title(self):
        """Return human-readable title of this resource.

        This is viewed in admin breadcrumbs path, etc.
        """
        title = getattr(self, "title", None)
        if title:
            return title

        raise NotImplementedError("get_breadcrumbs_title() implementation missing for {}".format(self))

    @classmethod
    def make_lineage(self, parent, child, name, allow_reinit=False):
        """Set traversing pointers between the child and the parent resources.

        Builds __parent__ and __name__ pointer and sets it on the child resource.
        """

        assert child
        assert parent
        assert name

        if not allow_reinit:
            # TODO:
            # We should not really allow this, but the at the moment unit tests reinialize admin object which in turn reinitializes all hardcoded model admin lineages. Fix it so that harcoded lineages are handled in more sane way.
            assert not getattr(child, "__parent__", None), "Tried to double init lineage for {} -> {}, previous parent was {}".format(parent, child, child.__parent__)

        child.__parent__ = parent
        child.__name__ = name
        return child


def     get_breadcrumb(context, request, root, current_view_name=None, current_view_url=None):
    """Traverse context up to the root element in the reverse order.

    :return: List of {url, name} dictionaries

    """

    elems = []

    # Looks like it is not possible to dig out the matched view from Pyramid request,
    # so we need to explicitly pass it if we want it to appear in URL
    if current_view_name:
        assert current_view_url
        elems.append(dict(url=current_view_url, name=current_view_name))

    while not isinstance(context, root):

        if not hasattr(context, "get_title"):
            raise RuntimeError("Breadcrumbs part missing get_title(): {}".format(context))

        elems.append(dict(url=request.resource_url(context), name=context.get_title()))

        if not hasattr(context, "__parent__"):
            raise RuntimeError("Broken traverse lineage on {}, __parent__ missing".format(context))

        if not isinstance(context, Resource):
            raise RuntimeError("Lineage has item not compatible with breadcrums: {}".format(context))

        context = context.__parent__

    # Add the last element
    elems.append(dict(url=request.resource_url(context), name=context.get_title()))
    elems.reverse()

    return elems