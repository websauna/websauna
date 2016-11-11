"""Mutable JSON list and dict tracking.

Based on Kotti CMS implementation:

* https://github.com/Kotti/Kotti/blob/5a33384e7b11994371c415b489edbec88ecbf044/kotti/sqla.py#L79
"""
import json

from sqlalchemy.ext.mutable import Mutable


def _default(obj):
    if isinstance(obj, MutationDict):
        return obj._d
    elif isinstance(obj, MutationList):
        return obj._d


def json_serializer(d):
    """MutationDict friendly json_serializer for create_enegine()

    See :py:meth:`websauna.system.model.meta.get_engine`.

    http://stackoverflow.com/a/36438671/315168
    """
    return json.dumps(d, default=_default)


class MutationDict(Mutable):
    """http://www.sqlalchemy.org/docs/orm/extensions/mutable.html
    """
    _wraps = dict

    def __init__(self, data):
        self._d = data
        super(MutationDict, self).__init__()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutationDict):
            if isinstance(value, dict):
                return cls(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __json__(self, request=None):
        return dict([(key, value.__json__(request))
                     if hasattr(value, '__json__') else (key, value)
                     for key, value in self._d.items()])


class MutationList(Mutable):

    _wraps = list

    def __init__(self, data):
        self._d = data
        super(MutationList, self).__init__()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutationList):
            if isinstance(value, list):
                return cls(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __radd__(self, other):
        return other + self._d

    def __json__(self, request=None):
        return [item.__json__(request) if hasattr(item, '__json__') else item
                for item in self._d]


def _make_mutable_method_wrapper(wrapper_class, methodname, mutates):
    def replacer(self, *args, **kwargs):
        method = getattr(self._d, methodname)
        value = method(*args, **kwargs)
        if mutates:
            self.changed()
        return value
    replacer.__name__ = methodname
    return replacer


for wrapper_class in (MutationDict, MutationList):
    for methodname, mutates in (
            ('__iter__', False),
            ('__len__', False),
            ('__eq__', False),
            ('__add__', False),
            ('__getitem__', False),
            ('__getslice__', False),
            ('__repr__', False),
            ('get', False),
            ('keys', False),

            ('__setitem__', True),
            ('__delitem__', True),
            ('__setslice__', True),
            ('__delslice__', True),
            ('append', True),
            ('clear', True),
            ('extend', True),
            ('insert', True),
            ('pop', True),
            ('setdefault', True),
            ('update', True),
            ('remove', True),
            ):
        # Only wrap methods that do exist on the wrapped type!
        if getattr(wrapper_class._wraps, methodname, False):
            setattr(
                wrapper_class, methodname,
                _make_mutable_method_wrapper(
                    wrapper_class, methodname, mutates),
                )


class NestedMixin(object):
    __parent__ = None

    def __init__(self, *args, **kwargs):
        self.__parent__ = kwargs.pop('__parent__', None)
        super(NestedMixin, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        value = self._d.__getitem__(key)
        return self.try_wrap(value)

    def changed(self):
        if self.__parent__ is not None:
            self.__parent__.changed()
        else:
            super(NestedMixin, self).changed()

    def try_wrap(self, value):
        for typ, wrapper in MUTATION_WRAPPERS.items():
            if isinstance(value, typ):
                value = wrapper(value, __parent__=self)
                break
        return value

    def __eq__(self, other):
        return self._d == other


class NestedMutationDict(NestedMixin, MutationDict):
    def setdefault(self, key, default):
        if isinstance(default, list):
            default = NestedMutationList(default, __parent__=self)
        elif isinstance(default, dict):
            default = NestedMutationDict(default, __parent__=self)
        return super(NestedMutationDict, self).setdefault(key, default)


class NestedMutationList(NestedMixin, MutationList):
    pass


MUTATION_WRAPPERS = {
    dict: NestedMutationDict,
    list: NestedMutationList,
}