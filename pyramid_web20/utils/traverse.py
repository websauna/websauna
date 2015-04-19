from abc import abstractmethod


class BreadcrumsResource:
    """Traversable resource which has get_title().

    TitledResource elements can form a breadcrumb chain.

    TODO: Don't use class hierarchy, convert this to adapter.
    """

    @abstractmethod
    def get_breadcrumbs_title(self):
        raise NotImplementedError("get_breadcrumbs_title() implementation missing for {}".format(self))



def make_lineage(parent, child, name):
    """Make sure traversing between objcts work as Pyramid resources."""

    if child is None:
        # The child is non-existing object, don't try to force lineage
        return None

    assert not hasattr(child, "__parent__"), "Tried to double init lineage for {} -> {}, previous parent was {}".format(parent, child, child.__parent__)

    child.__parent__ = parent
    child.__name__ = name


def get_breadcrumb(context, root):
    """Traverse context up to the root element in the reverse order."""

    elems = []
    while not isinstance(context, root):
        elems.append(context)

        if not hasattr(context, "__parent__"):
            raise RuntimeError("Broken traverse lineage on {}, __parent__ missing".format(context))

        if not isinstance(context, BreadcrumsResource):
            raise RuntimeError("Lineage has item not compatible with breadcrums: {}".format(context))

        context = context.__parent__

    elems.append(context)

    elems.reverse()

    return elems