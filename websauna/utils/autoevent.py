"""Automatically fire events on function enter and exit.

Use :py:func:`@event_source` to mark methods which fire events::

    class MyClass:

        # Target function
        @event_source
        def my_func(self):
            print("In myfunc")

        def run(self):
            self.my_func()

Create a class which can bind handlers to be called before and after event_source methods::

    class MyHandlers:

        # Aspect function
        @before(MyClass.my_func)
        def extra_logging(self):
            print("Entering my_func")

        # Aspect function
        @after(MyClass.my_func)
        def extra_logging(self):
            print("After my_func")


    # Nothing happens yet
    instance_a = MyClass()
    instance_a.run()
    # ... In myfunc

    # Aspects run on instiated targetters only
    my_handler = MyHandlers()

    instance_b = MyClass()
    bind_events(instance_b, my_handler)
    instance_b.run()
    # ...
    # Entering myfunc
    # In myfunc
    # After myfunc

This implementation

* It is not designed to be a general solution, but targets a very narrow use case only. But you are free to expand.

* Works only on class methods.

* Event sources are named. By default they get name from function name, but you can override this to avoid namespace conflict

* Event handlers are not called if the subclass of ``MyClass`` overrides the parent method and doesn't call ``super()``. In this case you need to call :py:func:`fire_advisor_event` manually from the overriden method.

"""
# Standard Library
import functools
import inspect
import typing as t
from collections import defaultdict
from enum import Enum


#: List of unbound methods that are marked as advisors
_advisor_methods = defaultdict(list)

#: Bound methods to be called when the join point is executed as [joint point name] -> (role, bound_method,)  mappings
_event_source_hooks = []


class AdvisorRole(Enum):
    """Mark the role when storing references to advisor methods in our internal registry."""

    #: This advisor is to be called before the function
    before = 1

    #: This advisor is to be called after the function
    after = 2


def fire_advisor_event(source: object, event_source_name: str, role: AdvisorRole, *args, **kwargs):
    """Call bound advisors for a join point."""

    advisor_mappings = getattr(source, "_advisor_mappings", None)
    if not advisor_mappings:
        # No advisors bound
        return

    advisors = advisor_mappings.get(event_source_name, [])

    for target_role, advisor in advisors:
        if target_role == role:
            advisor(*args, **kwargs)


def event_source(method: t.Callable, name: t.Optional[str]=None):
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
        _self = args[0]
        fire_advisor_event(_self, name, AdvisorRole.before)
        retval = method(*args, **kwargs)
        fire_advisor_event(_self, name, AdvisorRole.after)
        return retval

    assert name not in _event_source_hooks, "There already exist event_source with same name"

    _event_source_hooks.append(name)
    method._event_source_name = name

    return _inner


def after(target_event_source: t.Callable):
    """Call decorated function before target function.

    :param target_event_source: Target method decorated with @event_source
    """

    def _outer(advisor_method):

        wrapped = getattr(target_event_source, "__wrapped__", None)
        assert wrapped, "The target function {} was not decorated with @event_source decorator or any other decorator".format(target_event_source)

        name = wrapped._event_source_name

        _advisor_methods[advisor_method].append((AdvisorRole.after, name,))
        return advisor_method

    return _outer


def before(target_event_source: t.Callable):
    """Call decorated function before target function.

    :param target_event_source: Target method decorated with @event_source
    """

    def _outer(advisor_method):

        wrapped = getattr(target_event_source, "__wrapped__", None)
        assert wrapped, "The target function {} was not decorated with @event_source decorator or any other decorator".format(target_event_source)

        name = wrapped._event_source_name

        _advisor_methods[advisor_method].append((AdvisorRole.before, name,))
        return advisor_method

    return _outer


def bind_events(source: object, target: object):
    """Making the advisor functions of instance active.

    To correctly handle application flow, before and after advices are not bind their target functions until the instance of a target class is contructed. This avoids import time side effects that advices would be always unconditionally bound.

    :param source: Target instance providing @event_source methods

    :param target: Provider of advisor methods
    """
    cls = target.__class__  # noQA

    # Store bound advisors on the object using a private attribute
    mappings = getattr(source, "_advisor_mappings", None)
    if not mappings:
        source._advisor_mappings = mappings = defaultdict(list)

    for name, bound_advisor_method in inspect.getmembers(target, predicate=inspect.ismethod):
        unbound_method = bound_advisor_method.__func__

        if unbound_method in _advisor_methods:
            for role, name in _advisor_methods[unbound_method]:
                mappings[name].append((role, bound_advisor_method))
