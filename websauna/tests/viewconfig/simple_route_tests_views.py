# Pyramid
from pyramid.response import Response

# Websauna
from websauna.system.core.route import simple_route


# ``simple_route`` decorator can be used to associate view configuration
# information with a function, method, or class that acts as a Pyramid view
# callable.
@simple_route('/path/to/view')
def view_callable(request):
    return Response('Hello')


# You can set route name or any of view configuration arguments explicitly.
@simple_route(
    '/path/to/view/{arg}',
    route_name='foobar',
    request_method='POST',
    renderer='json')
def my_view(request):
    arg = request.matchdict["arg"]
    return {'message': 'Hello {}'.format(arg)}


# More than one decorator can be stacked on top of any number of others. Each
# decorator creates a separate route and view registration. It's better to
# provide ``route_name`` explicitly in this case.
@simple_route('/change', route_name='change')
@simple_route('/edit', route_name='edit')
def edit(request):
    return Response('edited!')


# ``simple_route` can be used as a class decorator.
@simple_route('/class-as-a-view')
class ClassAsAView(object):
    def __init__(self, request):
        self.request = request

    def __call__(self):
        return Response('class-as-a-view')


# The decorator can also be used against a method of a class.
class MyViewClass(object):

    # Class constructor must accept an argument list in one of two forms:
    #   * either a single argument, request, or
    #   * two arguments, context, request.
    def __init__(self, request):
        self.request = request

    # The method which is decorated must return a response.
    @simple_route('/amethod')
    def amethod(self):
        return Response('amethod')


# Using the decorator against a particular method of a class is equivalent to
# using the attr parameter in a decorator attached to the class itself.
@simple_route('/class-attr', attr='amethod')
class MyViewClassAttr(object):

    def __init__(self, request):
        self.request = request

    def amethod(self):
        return Response('class-attr')
