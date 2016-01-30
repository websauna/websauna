"""Helpers to traverse trees with __parent__ or __wrapped__ like attributes."""


def traverse_attribute(obj, attribute_name):
    """Turn a recursive parent traverse to a generator.

    E.g. if you have:

    .. code-block:: pycon

        >>> obj.__parent__ = parent
        >>> parent.__parent__ = grandparent

    You can turn this to list:

    .. code-block:: pycon

        >>> tree = traverse_attribute(obj, "__parent__")

        >>> list(tree)
        [obj, parent, grandparent]

    """

    while obj is not None:
        yield obj
        obj = getattr(obj, attribute_name, None)

