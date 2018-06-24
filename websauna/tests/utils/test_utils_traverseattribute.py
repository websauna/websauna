"""Test utils.traverseattribute."""
# Websauna
from websauna.utils import traverseattribute


class Dummy:
    """Dummy class to be traversed."""
    __parent__ = None


def test_traverse_attribute():
    """Test traverseattribute.traverse_attribute."""
    func = traverseattribute.traverse_attribute
    grandparent = Dummy()
    parent = Dummy()
    parent.__parent__ = grandparent
    obj = Dummy()
    obj.__parent__ = parent
    tree = list(func(obj, '__parent__'))

    assert len(tree) == 3
    assert tree[0] == obj
    assert tree[1] == parent
    assert tree[2] == grandparent
