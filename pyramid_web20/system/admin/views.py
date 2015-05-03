"""Admin interface main views. """
from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config
from pyramid_layout.panel import panel_config

from pyramid_web20.system import crud
from pyramid_web20.system.crud import views as crud_views
from pyramid_web20.system.crud import listing

from . import Admin
from . import ModelAdmin


from pyramid_web20.utils.panel import render_panel


@view_config(route_name='admin_home', renderer='admin/admin.html', permission='view')
def admin(request):

    admin = Admin.get_admin(request.registry)
    url = request.resource_url(admin)

    model_admins =  admin.model_admins.values()

    # TODO: Have renderer adapters for panels, so that they can override views
    rendered_panels = [render_panel(ma, request, name="admin_panel") for ma in model_admins]

    return dict(panels=rendered_panels)


@panel_config(name='admin_panel', context=ModelAdmin, renderer='admin/model_panel.html')
def default_model_admin_panel(context, request):
    model_admin = context
    count = model_admin.get_query().count()
    admin = model_admin.__parent__
    title = model_admin.title
    return locals()


class Listing(crud_views.Listing):
    """Base listing view for all admin models.

    """
    base_template = "admin/base.html"

    table = listing.Table(
        columns = [
            listing.Column("id", "Id",),
            listing.ControlsColumn()
        ]
    )

    @view_config(context=ModelAdmin, name="listing", renderer="crud/listing.html", route_name="admin", permission='view')
    def listing(self):
        # We override this method just to define admin route_name traversing
        return super(Listing, self).listing()



class Show(crud_views.Show):
    """Base listing view for all admin models.

    """
    base_template = "admin/base.html"

    @view_config(context=ModelAdmin.Resource, name="show", renderer="crud/show.html", route_name="admin", permission='view')
    def listing(self):
        # We override this method just to define admin route_name traversing
        return super(Show, self).show()




@view_config(context=ModelAdmin, name="", route_name="admin", permission='view')
def model_admin_default_view(context, request):
    """Redirect to listing if model admin URL is being accessed without a view name."""
    return HTTPFound(request.resource_url(context, "listing"))


@view_config(context=ModelAdmin.Resource, name="", route_name="admin", permission='view')
def model_resource_default_view(context, request):
    """Redirect to show if model instance URL is being accessed without a view name."""
    return HTTPFound(request.resource_url(context, "show"))