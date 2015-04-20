from abc import abstractmethod


class BreadcrumsResource:
    """Traversable resource which has get_title().

    TitledResource elements can form a breadcrumb chain.

    TODO: Don't use class hierarchy, convert this to adapter.
    """

    @abstractmethod
    def get_breadcrumbs_title(self):
        raise NotImplementedError("get_breadcrumbs_title() implementation missing for {}".format(self))



def make_lineage(parent, child, name, allow_reinit=False):
    """Make sure traversing between objcts work as Pyramid resources.

    Builds __parent__ pointer and sets it on the child object.
    """

    if child is None:
        # The child is non-existing object, don't try to force lineage upon it
        return None

    if not allow_reinit:
        # TODO:
        # We should not really allow this, but the at the moment unit tests reinialize admin object which in turn reinitializes all hardcoded model admin lineages. Fix it so that harcoded lineages are handled in more sane way.
        assert not hasattr(child, "__parent__"), "Tried to double init lineage for {} -> {}, previous parent was {}".format(parent, child, child.__parent__)

    child.__parent__ = parent
    child.__name__ = name
    return child


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