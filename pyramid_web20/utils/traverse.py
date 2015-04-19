


def make_lineage(parent, child, name):
    """Make sure traversing between objcts work as Pyramid resources."""

    if child is None:
        # The child is non-existing object, don't try to force lineage
        return None

    assert not hasattr(child, "__parent__"), "Tried to double init lineage for {} -> {}, previous parent was {}".format(parent, child, child.__parent__)

    child.__parent__ = parent
    child.__name__ = name