"""Admin interface. """
import copy

from pyramid.view import view_config, render_view

from pyramid.renderers import render

from pyramid_web20.utils import subview

from . import Admin
from . import ModelAdmin
from . import AdminPanel



@view_config(route_name='admin', renderer='admin/admin.html', permission='view')
def admin(request):
    admin = Admin.get_admin(request.registry)
    panels = list(admin.get_panels())

    # TODO: Handle permission errors here gracefully
    _request = copy.copy(request)
    _request.response = None
    rendered_panels = [subview.render_subview(p, "admin_panel", request) for p in panels]
    # rendered_panels = []
    return dict(panels=rendered_panels)


@view_config(context=AdminPanel, name="admin_panel", permission='view')
def panel(context, request):
    template_context = dict(panel=context)
    template = context.template
    return subview.render_template(template, template_context, request=request)


@view_config(context=ModelAdmin, name="listing", renderer='admin/x.html', permission='view')
def listing(request):
    admin = Admin.get_admin(request.registry)
    panels = [p.render(request) for p in admin.panels]

