"""

collanderalchemy: colanderalchemy.readthedocs.org/en/latest/

"""
import colander
from collections import OrderedDict
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.request import Request
from pyramid.view import view_config

from websauna.compat import typing

import deform

from websauna.system.core import messages
from websauna.system.form.colander import PropertyAwareSQLAlchemySchemaNode

from . import sqlalchemy, Resource
from . import paginator
from . import CRUD





class ResourceButton:
    """Present a button on the top right corner of CRUD views.

    These buttons, with breadcrumbs, form the basic navigation inside the CRUD management interface.

    Buttons are permission-aware, so they are rendered only when the user has required permission.
    """

    #: The template used to render this button. Also overridable through the constructor.
    template = "crud/resource_button.html"

    def __init__(self, id:str=None, name:str=None, template:str=None, permission:str=None):
        """
        :param id: Id of the button to be used as HTML id
        :param name:  Human readable label of the button
        :param template: Override template for this button
        :param permission: You need to have named permission on the context to make this button visible. Set to none to make the button appear always.
        """

        assert id, "Button id missing"
        assert name, "Button name missing"

        self.id = id
        self.name = name

        self.permission = permission

        if template:
            self.template = template

    def is_visible(self, context, request):
        if self.permission:
            return request.has_permission(self.permission, context)
        else:
            return True

    def get_link(self, context:Resource, request:Request) -> str:
        """Generate a link where this button is pointing at."""
        return "#"

    def render(self, context:Resource, request:Request) -> str:
        """Return HTML code for this button."""
        template_context = dict(context=context, button=self)
        return render(self.template, template_context, request=request)


class TraverseLinkButton(ResourceButton):
    """A button which is a link to another page on this resource."""

    def __init__(self, view_name:str, **kwargs):
        """
        :param view_name: request.resource_url() view name where this button points at
        :param kwargs: Other ResourceButton construction arguments
        """
        super(TraverseLinkButton, self).__init__(**kwargs)
        self.view_name = view_name

    def get_link(self, context, request):
        return request.resource_url(context, self.view_name)


class CRUDView:
    """Base class for different CRUD views.

    This includes views having context as the listing and having context as the individual item."""

    #: base_template may point into a template providing ``crud_content`` block where the contents of the view is rendered. This allows you to decorate your CRUD which a specific page frame.
    base_template = None

    #: Instance of ResourceButtons which appear on the top right corner of this view
    resource_buttons = []

    def get_resource_buttons(self) -> typing.List:
        """Get the context-sensitive button options presented on this page.

        These are usually links to "Show", "Edit", "Delete" of the formm context, but you are free to add your own buttons here. The buttons are usually placed on the top right corner of the form.

        Unless you want to dynamically generate buttons depending on the page, it is enough to set ``resource_buttons`` attribute on the view class.

        :return: OrderedDict instance where key is button id and value is the link to where the button points.
        """
        return self.resource_buttons


class Listing(CRUDView):
    """View class to render item list in CRUD."""

    #: Instance of websauna.crud.listing.Table describing how the list should be rendered
    table = None

    #: How the result of this list should be split to pages
    paginator = paginator.DefaultPaginator()

    resource_buttons = [TraverseLinkButton(id="add", name="Add", view_name="add", permission="add")]

    def __init__(self, context, request):
        """
        :param context: Points to ``CRUD`` instance.
        :param request:
        """
        self.context = context
        self.request = request

    def get_crud(self) -> CRUD:
        return self.context

    def get_model(self) -> object:
        return self.context.get_model()

    def get_query(self):
        """Get SQLAlchemy query used in this CRUD listing.

        This can include filtering e.g. request user, crud parameters, so on.
        """
        return self.context.get_query()

    def get_count(self, query):
        """Calculate total item count based on query."""
        return query.count()

    def order_query(self, query):
        """Sort the query."""
        return query

    def get_title(self) -> str:
        """Get the user-readable name of the listing view (breadcrumbs, etc.)"""
        return "All {}".format(self.get_crud().plural_name)

    def paginate(self, query, template_context):
        """Create template variables for paginatoin results."""
        total_items =  self.get_count(query)
        batch = self.paginator.paginate(query, self.request, total_items)
        template_context["batch"] = batch
        template_context["count"] = total_items

    @view_config(context=sqlalchemy.CRUD, name="listing", renderer="crud/listing.html", permission='view')
    def listing(self):
        """View for listing model contents in CRUD."""

        crud = self.context

        table = self.table
        columns = table.get_columns()

        # Some pre-render sanity checks

        if not columns:
            raise RuntimeError("CRUD listing doesn't not define any columns: {}".format(self.context))

        for c in columns:
            if not c.header_template:
                raise RuntimeError("header_template missing for column: {}".format(c))

        query = self.get_query()
        query = self.order_query(query)
        base_template = self.base_template

        # This is to support breadcrums with titled views
        current_view_name = title = self.get_title()

        title = self.context.title
        count =  self.get_count(query)
        # Base listing template variables
        template_vars = dict(title=title, columns=columns, base_template=base_template, query=query, crud=crud, current_view_name=current_view_name, resource_buttons=self.get_resource_buttons(), count=count)

        # Include pagination template context
        # self.paginate(query, template_vars)

        return template_vars



class FormView(CRUDView):
    """A base class for views which utilize ColanderAlchemy to view/edit SQLAlchemy model instances."""

    #: If the child class is not overriding the rendering loop, point this to a template which provides the page frame and ``crud_content`` block.
    base_template = None

    #: List of SQLAlchemy and JSONProperty field names automatically mapped to a form
    includes = ["id",]

    def __init__(self, context, request):
        """
        :param context: Instance of ``traverse.Resource()`` or its subclasses
        :param request: HTTP request
        """
        self.context = context
        self.request = request

    def create_form(self, buttons=()):
        """Automatically create a Deform form based on the underlying SQLALchemy model.

        We read ``self.includes`` for field names and colander.SchemaNode objects which should appear in the form.

        The automatically generated form schema can be customized by subclass ``customize_schema()`` and ``bind_schema()`` hooks.

        :param buttons: Passed to Deform as form buttons
        """
        model = self.get_model()
        includes = self.includes
        schema = PropertyAwareSQLAlchemySchemaNode(model, includes=includes)
        self.customize_schema(schema)
        schema = self.bind_schema(schema)
        form = deform.Form(schema, buttons=buttons)
        return form

    def bind_schema(self, schema):
        """Initialize Colander field dynamic default values. By default, don't do anything."""
        return schema

    def get_crud(self):
        """Get CRUD manager object for this view."""
        return self.context.__parent__

    def get_model(self):
        return self.get_crud().get_model()

    def get_object(self):
        """Get underlying SQLAlchemy model instance from current Pyramid traversing context."""
        return self.context.get_object()

    def get_title(self):
        """Get human-readable title for for template page title."""
        return "#{}".format(self.get_object().id)

    def customize_schema(self, schema):
        """After Colander schema is automatically generated from the SQLAlchemy model, edit it in-place for fine-tuning.

        Override this in your view subclass for schema customizations.
        """
        return



class Show(FormView):
    """Read-only view to SQLAlchemy model instance using Deform form generated by ColanderAlchemy.
    """

    resource_buttons = [TraverseLinkButton(id="edit", name="Edit", view_name="edit")]

    def get_title(self):
        return "#{}".format(self.get_object().id)

    @view_config(context=sqlalchemy.Resource, name="show", renderer="crud/show.html", permission='view')
    def show(self):
        """View for showing an individual object."""

        obj = self.context.get_object()
        base_template = self.base_template

        form = self.create_form()
        appstruct = form.schema.dictify(obj)
        rendered_form = form.render(appstruct, readonly=True)

        resource_buttons = self.get_resource_buttons()

        crud = self.get_crud()

        title = current_view_name = self.get_title()

        return dict(form=rendered_form, context=self.context, obj=obj, title=title, crud=crud, base_template=base_template, resource_buttons=resource_buttons)


class Edit(FormView):
    """Edit SQLAlchemy model instance using Deform form generated by ColanderAlchemy.
    """

    resource_buttons = [TraverseLinkButton(id="show", name="Show", view_name="show")]

    # We display id field on the edit form and it needs special handling, because it is read-only
    # See http://deformdemo.repoze.org/readonly_value_nonvalidation/
    includes = [
        colander.SchemaNode(colander.String(),
            name="id",
            missing=lambda node, kw: kw["obj"].id,
            widget=deform.widget.TextInputWidget(readonly=True),
        )
    ]

    def get_title(self):
        return "Editing #{}".format(self.get_object().id)

    def create_form(self):
        return super(Edit, self).create_form(buttons=("save", "cancel",))

    def bind_schema(self, schema):
        return schema.bind(obj=self.context.get_object())

    def do_success(self):
        """Called after the save (objectify) has succeeded.

        :return: HTTPResponse
        """
        messages.add(self.request, kind="success", msg="Changes saved.")

        # Redirect back to view page after edit page has succeeded
        return HTTPFound(self.request.resource_url(self.context, "show"))

    def do_cancel(self):
        """Called when user presses the cancel button.

        :return: HTTPResponse
        """

        # Redirect back to view page after edit page has succeeded
        return HTTPFound(self.request.resource_url(self.context, "show"))

    @view_config(context=sqlalchemy.Resource, name="edit", renderer="crud/edit.html", permission='edit')
    def edit(self):
        """View for showing an individual object."""

        # SQLAlchemy model instance
        obj = self.context.get_object()
        base_template = self.base_template

        # Create form, convert instance to Colander structure for Deform
        form = self.create_form()

        crud = self.get_crud()

        title = current_view_name = self.get_title()

        if "save" in self.request.POST:

            controls = self.request.POST.items()

            try:

                appstruct = form.validate(controls)

                # Cannot update id, as it is read-only
                if 'id' in appstruct:
                    del appstruct["id"]

                form.schema.objectify(appstruct, obj)

                return self.do_success()

            except deform.ValidationFailure as e:
                # Whoops, bad things happened, render form with validation errors
                rendered_form = e.render()

        elif "cancel" in self.request.POST:
            # User pressed cancel
            return self.do_cancel()
        else:
            # Render initial form view with populated values
            appstruct = form.schema.dictify(obj)
            rendered_form = form.render(appstruct)

        return dict(form=rendered_form, context=self.context, obj=obj, title=title, crud=crud, base_template=base_template, resource_buttons=self.get_resource_buttons())


class Add(FormView):
    """Create a new SQLAlchemy instance."""

    #: List of SQLAlchemy and JSONProperty field names automatically mapped to a form
    includes = []

    def get_title(self):
        return "Add new {}".format(self.get_crud().singular_name)

    def create_form(self):
        return super(Add, self).create_form(buttons=("add", "cancel",))

    def get_crud(self):
        """Get CRUD manager object for this view."""
        return self.context

    def get_model(self):
        return self.get_crud().get_model()

    def create_object(self):
        """Create new empty object to be populated from the form."""
        model = self.get_model()
        return model()

    def save_object(self, obj):
        """Put newly created object to persist storage."""
        DBSession.add(obj)
        DBSession.flush()

    @view_config(context=sqlalchemy.CRUD, name="add", renderer="crud/add.html", permission='add')
    def add(self):
        """View for showing an individual object."""

        # SQLAlchemy model instance
        base_template = self.base_template

        # Create form, convert instance to Colander structure for Deform
        form = self.create_form()

        crud = self.get_crud()

        title = current_view_name = self.get_title()

        resource_buttons = self.get_resource_buttons()

        if "add" in self.request.POST:

            controls = self.request.POST.items()

            try:
                appstruct = form.validate(controls)

                # Cannot update id, as it is read-only
                if 'id' in appstruct:
                    del appstruct["id"]

                obj = self.create_object()

                form.schema.objectify(appstruct, obj)

                # We do not need to explicitly call save() or commit() as we are using Zope transaction manager
                self.save_object(obj)

                messages.add(self.request, kind="success", msg="Item added.")

                resource = crud.wrap_to_resource(obj)

                # Redirect back to view page after edit page has succeeded
                return HTTPFound(self.request.resource_url(resource, "show"))

            except deform.ValidationFailure as e:
                # Whoops, bad things happened, render form with validation errors
                rendered_form = e.render()

        elif "cancel" in self.request.POST:
            # User pressed cancel
            return HTTPFound(self.request.resource_url(self.get_crud(), "listing"))
        else:
            # Render initial form view with populated values
            rendered_form = form.render()

        return dict(form=rendered_form, context=self.context, title=title, crud=crud, base_template=base_template, resource_buttons=self.get_resource_buttons())

