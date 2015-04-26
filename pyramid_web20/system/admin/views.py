"""Admin interface. """
import copy
from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config, render_view
from pyramid.traversal import resource_path
from pyramid.renderers import render

from pyramid_web20.utils import subview
from pyramid_web20.system import crud
from pyramid_web20.system.crud import views as crud_views

from . import Admin
from . import ModelAdminCRUD
from . import AdminPanel


@view_config(route_name='admin_home', renderer='admin/admin.html', permission='view')
def admin(request):

    admin = Admin.get_admin(request.registry)
    url = request.resource_url(admin)

    panels = list(admin.get_panels())

    # TODO: Have renderer adapters for panels, so that they can override views
    rendered_panels = [panel(p, request) for p in panels]
    # rendered_panels = []
    return dict(panels=rendered_panels)


@view_config(context=AdminPanel, name="admin_panel", permission='view')
def panel(context, request):
    model_admin = context.__parent__
    count = model_admin.get_query().count()
    admin = model_admin.__parent__
    template_context = dict(panel=context, count=count, model_admin=model_admin, crud=context, admin=admin)
    template = context.template
    return subview.render_template(template, template_context, request=request)



class AdminCRUDViewController(crud_views.SQLAlchemyCRUDViewController):

    @view_config(context=crud.Listing, renderer="crud/listing.html", route_name="admin", permission='view')
    def listing(self):
        # We override this method just to define admin route_name traversing
        return super(AdminCRUDViewController, self).listing(base_template="admin/base.html")

    @view_config(context=crud.Instance, renderer="crud/show.html", route_name="admin", permission='view')
    def show(self):
        # We override this method just to define admin route_name traversing
        return super(AdminCRUDViewController, self).show(base_template="admin/base.html")

    @view_config(context=ModelAdminCRUD, route_name="admin", permission='view')
    def default(self):
        """Redirect to the user listing as the default action. """
        r = HTTPFound(self.request.resource_url(self.context.listing))
        return r







