"""Automatically fire events on function enter and exit.

This little helper is inspired by `aspect oriented programming <https://en.wikipedia.org/wiki/Aspect-oriented_programming>`_. It allows you to insert before and after hooks for function calls.

Example::

    class MyClass:

        # Target function
        @join_point
        def my_func(self):
            print("In myfunc")

        def run(self):
            self.my_func()


    class MyAspects(metaclass=Crosscutter):

        # Aspect function
        @advice_before(MyClass.my_func)
        def extra_logging(self):
            print("Entering my_func")

        # Aspect function
        @advice_after(MyClass.my_func)
        def extra_logging(self):
            print("After my_func")


    # Nothing happens yet
    instance_a = MyClass()
    instance_a.run()
    # ... In myfunc

    # Aspects run on instiated crosscutters only
    my_aspect_provider = MyAspects()

    instance_b = MyClass()
    instance_b.run()
    # ...
    # Entering myfunc
    # In myfunc
    # After myfunc

This implementation

* It is not designed to be a general solution, but targets a very narrow use case only. But you are free to expand.

* Works only on class methods.

* Crosscutter provided advisor methods are not called until at least one instance Crosscutter is created.

* Join points get automatically name by from function name, but you can override this to avoid namespace conflict

* Aspects are not called if the subclass of ``MyClass`` overrides the parent method and doesn't call ``super()``. In this case you need to call :py:func:`fire_aspect_event` manually from the overriden method.

"""
import inspect
from enum import Enum

import functools

from websauna.compat.typing import Callable
from websauna.compat.typing import Optional

#: List of unbound methods that are marked as advisors
_advisor_methods = dict()

#: Bound methods to be called when the join point is executed as [joint point name] -> (role, bound_method,)  mappings
_join_point_hooks = dict()


class AdvisorRole(Enum):
    """Mark the role when storing references to advisor methods in our internal registry."""

    #: This advisor is to be called before the function
    before = 1

    #: This advisor is to be called after the function
    after = 2


def fire_aspect_event(join_point_name: str, role: AdvisorRole, *args, **kwargs):
    """Call bound advisors for a join point."""

    for target_role, advisor in _join_point_hooks.get(join_point_name, []):
        if target_role == role:
            advisor(*args, **kwargs)


def join_point(method: Callable, name: Optional[str]=None):
    """A decorator which makes the function act as a source of before and after call events.

    You can later subscribe to these event with :py:func:`before` and :py:func`after` decorators.

    :param method: Target class method

    :param: Name of for the join point. If not given use the function name.
    """

    # We must use function name instead of function pointer for the registry, because function object changes with unbound vs. bound Python class methods

    if not name:
        name = method.__name__

    @functools.wraps(method)
    def _inner(*args, **kwargs):
        fire_aspect_event(name, AdvisorRole.before)
        retval = method(*args, **kwargs)
        fire_aspect_event(name, AdvisorRole.after)
        return retval

    _join_point_hooks[name] = []
    method._join_point_name = name

    return _inner


def advice_after(target_join_point: Callable):
    """Call decorated function before target function.

    :param target_join_point: Target method decorated with @join_point
    """

    def _outer(advisor_method):

        wrapped = getattr(target_join_point, "__wrapped__", None)
        assert wrapped, "The target function {} was not decorated with @join_point decorator or any other decorator".format(target_join_point)

        name = wrapped._join_point_name

        _advisor_methods[advisor_method] = (AdvisorRole.after, name,)
        return advisor_method

    return _outer


def advice_before(target_join_point: Callable):
    """Call decorated function before target function.

    :param target_join_point: Target method decorated with @join_point
    """

    def _outer(advisor_method):

        wrapped = getattr(target_join_point, "__wrapped__", None)
        assert wrapped, "The target function {} was not decorated with @join_point decorator or any other decorator".format(target_join_point)

        name = wrapped._join_point_name

        _advisor_methods[advisor_method] = (AdvisorRole.before, name,)
        return advisor_method

    return _outer


class Crosscutter(type):
    """Metaclass for binding aspect advices.

    To correctly handle application flow, before and after advices are not bind their target functions until the instance of a target class is contructed. This avoids import time side effects that advices would be always unconditionally bound.

    http://eli.thegreenplace.net/2011/08/14/python-metaclasses-by-example
    """

    def __call__(cls, *args, **kwds):
        instance = type.__call__(cls, *args, **kwds)
        Crosscutter.bind_aspects(cls, instance)
        return instance

    @staticmethod
    def bind_aspects(cls, instance):
        """Translate unbound advisors to bound method advisors."""
        for name, bound_method in inspect.getmembers(instance, predicate=inspect.ismethod):
            unbound_method = bound_method.__func__
            if unbound_method in _advisor_methods:
                role, joint_point = _advisor_methods[unbound_method]
                _join_point_hooks[joint_point].append((role, bound_method,))
