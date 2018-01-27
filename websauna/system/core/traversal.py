"""Traversing core logic."""
# Pyramid
from pyramid.interfaces import ILocation
from zope.interface import implementer


@implementer(ILocation)
class Resource:
    """Traversable resource in a nested tree hierarchy with basic breadcrumbs support.

    All traverable context classes should inherit from this class. Note that this is not a strict requirement, as often anything implementing :py:class:`pyramid.interfaces.ILocation` and ``get_title()`` will work.

    For more information see :ref:`Traversal <traversal>`.

    ..  _traversal:
    """

    # TODO: Cannot annotate request as it breaks sphinx-autodoc-typehints, sphinx-autodoc-typehints==1.1.0, when doing make html
    def __init__(self, request):

        #: Pointer to the parent object in traverse hierarchy. This is none until make_lineage is called.
        self.__parent__ = None

        #: The id of this resource as its appear in URL and traversing path
        self.__name__ = None

        self.request = request

    def get_title(self) -> str:
        """Return human-readable title of this resource.

        This is viewed in admin breadcrumbs path, etc.
        """
        title = getattr(self, "title", None)
        if title:
            return title

        raise NotImplementedError("get_title() implementation missing for {}".format(self))

    @classmethod
    def make_lineage(self, parent, child, name, allow_new_parent=False) -> "Resource":
        """Set traversing pointers between the child and the parent resources.

        Builds __parent__ and __name__ pointer and sets it on the child resource.

        * If lineage relationship is not lazy and the referenced children is stored in the parent, the lineage must be set when the child is put into parent container.

        * If lineage relationship is lazy and child resource is constructed upon lookup in ``__item__``, the lineage is constructed before the child is returned.

        :param parent: Parent resource who children is become part to

        :param child: Child resource mutated in place

        :param name: Id of the child resource as it will appear in the URL traversing path

        :param allow_new_parent: If the child has alraedy a parent assigned, allow override the parent... or basically move an existing resource. You don't usually want this for in-memory resource and this is for catching bugs.

        :return: The mutated child resource
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
