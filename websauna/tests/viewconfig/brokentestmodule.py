"""A broken module where we try to override view class which does not defined views."""
# Websauna
from websauna.system.core.viewconfig import view_overrides


class ParentResource:
    id = "parent"


class ChildResource(ParentResource):
    id = "child"


class ParentView:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # No views defined


@view_overrides(context=ChildResource)
class ChildView(ParentView):
    pass


class Root:
    """Traversing root."""

    def __init__(self, request):
        pass

    def __getitem__(self, name):
        if name == "parent":
            return ParentResource()
        elif name == "child":
            return ChildResource()
