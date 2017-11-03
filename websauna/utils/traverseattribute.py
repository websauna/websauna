"""Helpers to traverse trees with __parent__ or __wrapped__ like attributes."""


def traverse_attribute(obj, attribute_name):
    """Turn a recursive parent traverse to a generator.

    E.g. if you have:

    .. code-block:: python

        >>> class Dummy:
        ...     __parent__ = None
        ...
        >>> grandparent = Dummy()
        >>> parent = Dummy()
        >>> parent.__parent__ = grandparent
        >>> obj = Dummy()
        >>> obj.__parent__ = parent

    You can turn this to a list:

    .. code-block:: python

        >>> tree = traverse_attribute(obj, "__parent__")
        >>> list(tree)
        [obj, parent, grandparent]

    """

    while obj is not None:
        yield obj
        obj = getattr(obj, attribute_name, None)
