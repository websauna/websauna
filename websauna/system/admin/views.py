"""Admin interface main views. """
# Pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_layout.panel import panel_config

# Websauna
from websauna.system.admin.modeladmin import ModelAdmin
from websauna.system.admin.modeladmin import ModelAdminRoot
from websauna.system.admin.utils import get_admin
from websauna.system.core.panel import render_panel
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import views as crud_views
from websauna.system.crud import listing
from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator
from websauna.system.crud.sqlalchemy import sqlalchemy_deleter
from websauna.system.crud.views import TraverseLinkButton


@view_config(route_name='admin_home', renderer='admin/admin.html', permission='view')
def admin(request):
    """Admin front page page."""

    admin = get_admin(request)

    # For now, admin panels always appear in ascending order

    model_admin_root = admin["models"]

    # TODO: Have renderer adapters for panels, so that they can override views
    admin_panels = sorted(model_admin_root.items(), key=lambda pair: pair[1].title)
    rendered_panels = [render_panel(ma, request, name="admin_panel") for id, ma in admin_panels]

    return dict(panels=rendered_panels)


@panel_config(name='admin_panel', context=ModelAdmin, renderer='admin/model_panel.html')
def default_model_admin_panel(context, request, **kwargs):
    """Generic panel for any model admin.

    Display count of items in the database.
    """
    model_admin = context
    count = model_admin.get_query().count()
    admin = model_admin.__parent__
    title = model_admin.title
    return dict(locals(), **kwargs)


class Listing(crud_views.Listing):
    """Base listing view for all admin models.

    """
    base_template = "admin/base.html"

    table = listing.Table(
        columns=[
            listing.Column(id="id", name="Id",),
            listing.StringPresentationColumn(id="value", name="Value"),
            listing.ControlsColumn()
        ]
    )

    @property
    def title(self):
        return "All {}".format(self.context.title)

    @view_config(context=ModelAdmin, name="listing", renderer="crud/listing.html", route_name="admin", permission='view')
    def listing(self):
        # We override this method just to define admin route_name traversing
        return super(Listing, self).listing()


class Show(crud_views.Show):
    """Default show view for model admin."""
    base_template = "admin/base.html"

    form_generator = SQLAlchemyFormGenerator()

    resource_buttons = [
        TraverseLinkButton(id="edit", name="Edit", view_name="edit", permission="edit"),
        TraverseLinkButton(id="delete", name="Delete", view_name="delete", permission="delete"),
        TraverseLinkButton(id="shell", name="Shell", view_name="shell", permission="shell", tooltip="Open IPython Notebook shell and have this item prepopulated in obj variable.", feature="notebook"),
    ]

    @view_config(context=ModelAdmin.Resource, name="show", renderer="crud/show.html", route_name="admin", permission='view')
    def show(self):
        # We override this method just to define admin route_name traversing
        return super(Show, self).show()


class Edit(crud_views.Edit):
    """Default edit vie for model admin."""
    base_template = "admin/base.html"

    form_generator = SQLAlchemyFormGenerator()

    @view_config(context=ModelAdmin.Resource, name="edit", renderer="crud/edit.html", route_name="admin", permission='edit')
    def edit(self):
        # We override this method just to define admin route_name traversing
        return super(Edit, self).edit()


class Add(crud_views.Add):
    """Default add view for model admin."""
    base_template = "admin/base.html"

    form_generator = SQLAlchemyFormGenerator()

    @view_config(context=ModelAdmin, name="add", renderer="crud/add.html", route_name="admin", permission='add')
    def add(self):
        # We override this method just to define admin route_name traversing
        return super(Add, self).add()


@view_overrides(context=ModelAdmin.Resource, route_name="admin")
class Delete(crud_views.Delete):
    """Delete view for SQLAlchemy model admins."""

    base_template = "admin/base.html"

    deleter = sqlalchemy_deleter


@view_config(context=ModelAdmin, name="", route_name="admin", permission='view')
def model_admin_default_view(context, request):
    """Redirect to listing if model admin URL is being accessed without a view name."""
    return HTTPFound(request.resource_url(context, "listing"))


@view_config(context=ModelAdmin.Resource, name="", route_name="admin", permission='view')
def model_resource_default_view(context, request):
    """Redirect to show if model instance URL is being accessed without a view name."""
    return HTTPFound(request.resource_url(context, "show"))


@view_config(route_name='admin', context=ModelAdminRoot, permission='view')
def view__model_admin_root(context, request):
    """Model admin root does not have a view per se so we redirect to admin root."""
    return HTTPFound(request.resource_url(context.__parent__))
