"""A test URL you can call to cause a production run time error."""

from pyramid.view import view_config

@view_config(route_name='error_trigger')
def error_trigger(request):
    """An error logging view to generate a run-time error."""
    raise RuntimeError("Test error.")