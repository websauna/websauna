"""Traversing definitions."""
from pyramid.request import Request
from websauna.system.core.interfaces import IRoot
from zope.interface import Interface


class Resource:
    """Traversable resource part.

    Wraps underlying object into a traverse path. All resources are also tied to ``request`` object which gives them ability to query databases for further traversing through ``__getitem__()``.
    """

    def __init__(self, request):

        #: Pointer to the parent object in traverse hierarchy. This is none until make_lineage is called.
        self.__parent__ = None

        #: The id of this resource as its appear in URL and traversing path
        self.__name__ = None

        self.request = request

    def get_title(self):
        """Return human-readable title of this resource.

        This is viewed in admin breadcrumbs path, etc.
        """
        title = getattr(self, "title", None)
        if title:
            return title

        raise NotImplementedError("get_breadcrumbs_title() implementation missing for {}".format(self))

    @classmethod
    def make_lineage(self, parent, child, name, allow_new_parent=False):
        """Set traversing pointers between the child and the parent resources.

        Builds __parent__ and __name__ pointer and sets it on the child resource.

        * If lineage relationship is not lazy and the referenced children is stored in the parent, the lineage must be set when the child is put into parent container.

        * If lineage relationship is lazy and child resource is constructed upon lookup in ``__item__``, the lineage is constructed before the child is returned.

        :param parent: Parent resource who children is become part to

        :param child: Child resource mutated in place

        :param name: Id of the child resource as it will appear in the URL traversing path

        :param allow_new_parent: If the child has alraedy a parent assigned, allow override the parent... or basically move an existing resource. You don't usually want this for in-memory resource and this is for catching bugs.
        """

        assert child
        assert parent
        assert name

        if not allow_new_parent:
            # Catch bugs when you try to double lineage a persistnet parent -> child relationship
            assert not getattr(child, "__parent__", None), "Tried to double init lineage for {} -> {}, previous parent was {}".format(parent, child, child.__parent__)

        child.__parent__ = parent
        child.__name__ = name
        return child
