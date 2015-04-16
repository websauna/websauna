"""Admin interface. """
from pyramid.view import view_config


@view_config(route_name='admin', renderer='admin/admin.html', permission='view')
def admin(self):
    """ """
    return {}


@view_config(route_name='admin_model', renderer='admin/admin.html')
def admin_model(self):
    """ """
    return {}
