# Pyramid
from pyramid.httpexceptions import HTTPOk
from pyramid.view import view_config

# Websauna
from websauna.system.core.viewconfig import view_overrides


class ParentResource:
    id = "parent"


class ChildResource(ParentResource):
    id = "child"


class ChildResource2(ParentResource):
    id = "child2"


class GrandChildResource(ChildResource):
    id = "grand_child"


class GrandGrandChildResource(GrandChildResource):
    id = "grand_grand_child"


class ParentView:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name="edit", context=ParentResource)
    def traversing_test(self):
        return HTTPOk("Editing: {}".format(self.context.id))


@view_overrides(context=ChildResource)
class ChildView(ParentView):
    pass


@view_overrides(context=GrandChildResource)
class GrandChildView(ParentView):
    pass


@view_overrides(context=GrandGrandChildResource)
class GrandChildView(GrandChildView):
    pass


@view_overrides(context=ChildResource2)
class ChildViewWithOtherViewConfigs(ParentView):

    @view_config(name="show", context=ChildResource2)
    def traversing_test(self):
        return HTTPOk("Showing: {}".format(self.context.id))


class Root:
    """Traversing root."""

    def __init__(self, request):
        pass

    def __getitem__(self, name):
        if name == "parent":
            return ParentResource()
        elif name == "child":
            return ChildResource()
        elif name == "child2":
            return ChildResource2()
        elif name == "grand_child":
            return GrandChildResource()
        elif name == "grand_grand_child":
            return GrandGrandChildResource()


class ParentRouteView:

    def __init__(self, request):
        pass

    @view_config(route_name="parent_hello", renderer="parent.html")
    def traversing_test(self):
        return {"class": self.__class__.__name__}


@view_overrides(route_name="child_hello", renderer="child.html")
class ChildRouteView(ParentRouteView):
    pass
