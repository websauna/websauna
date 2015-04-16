"""Admin interface. """
from pyramid.view import view_config


@view_config(route_name='admin')
def admin(self):
    """ """
    return {}
