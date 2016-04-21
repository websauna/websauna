"""Default CRUD views."""
import colander
from abc import abstractmethod

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import Query

import deform

from websauna.compat import typing
from websauna.system.core import messages
from websauna.system.form import interstitial
from websauna.system.form.fieldmapper import EditMode

from . import paginator
from . import Resource
from . import CRUD


class ResourceButton:
    """Present a button on the top right corner of CRUD views.

    These buttons, with breadcrumbs, form the basic navigation inside the CRUD management interface.

    Buttons are permission-aware, so they are rendered only when the user has required permission.
    """

    #: The template used to render this button. Also overridable through the constructor.
    template = "crud/resource_button.html"

    def __init__(self, id:str=None, name:str=None, template:str=None, permission:str=None, tooltip:str=None):
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
        self.tooltip = tooltip

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
    """List items in CRUD."""

    #: Instance of :py:class:`websauna.crud.listing.Table` describing how the list should be rendered
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

    def get_query(self) -> Query:
        """Get SQLAlchemy query used in this CRUD listing.

        This can include filtering e.g. request user, crud parameters, so on.
        """
        return self.context.get_query()

    def get_count(self, query:Query):
        """Calculate total item count based on query."""
        return query.count()

    def order_query(self, query:Query):
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

    @view_config(context=CRUD, name="listing", renderer="crud/listing.html", permission='view')
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
        template_vars = dict(title=title, columns=columns, base_template=base_template, query=query, crud=crud, current_view_name=current_view_name, resource_buttons=self.get_resource_buttons(), count=count, view=self)

        # Include pagination template context
        # self.paginate(query, template_vars)

        return template_vars



class FormView(CRUDView):
    """An abstract base class for form-based CRUD views.

    Use Deform form library. This views is abstract and it does not have dependency to any underlying model system like SQLAlchemy.
    """
    #: If the child class is not overriding the rendering loop, point this to a template which provides the page frame and ``crud_content`` block. For example use see :py:class:`websauna.system.user.adminviews.UserAdd`.
    base_template = None

    #: This is an instance of :py:class:`websauna.system.crud.formgenerator.FormGenerator`. For SQLAlchemy models it is :py:class:`websauna.system.crud.formgenerator.SQLAlchemyFormGenerator`. Form generator describers how a CRUD model is turned to a Deform form. It is called by :py:meth:`create_form`. For example use cases see e.g. :py:class:`websauna.system.user.adminviews.UserAdd`.
    form_generator = None

    def __init__(self, context:Resource, request:Request):
        """
        :param context: Instance of ``traverse.Resource()`` or its subclasses
        :param request: HTTP request
        """
        self.context = context
        self.request = request

    def create_form(self, mode:EditMode, buttons=(), nested=None) -> deform.Form:
        model = self.get_model()
        assert getattr(self, "form_generator", None), "Class {} must define a form_generator".format(self)
        return self.form_generator.generate_form(request=self.request, context=self.context, model=model, mode=mode, buttons=buttons)

    @abstractmethod
    def get_form(self):
        """Create the form object for a view.

        Subclasses most override this, call ``create_form()`` and pass correct edit mode and buttons.
        """

    def get_crud(self) -> CRUD:
        """Get CRUD manager object for this view."""
        return self.context.__parent__

    def get_model(self) -> type:
        """Get SQLAlchemy model we are managing."""
        return self.get_crud().get_model()

    def get_object(self):
        """Get underlying SQLAlchemy model instance from current Pyramid traversing context."""
        return self.context.get_object()

    def get_title(self):
        """Get human-readable title for for template page title."""
        return "#{}".format(self.get_object().id)

    def customize_schema(self, schema:colander.Schema):
        """After Colander schema is automatically generated from the SQLAlchemy model, edit it in-place for fine-tuning.

        Override this in your view subclass for schema customizations.
        """
        pass

    def pull_in_widget_resources(self, form:deform.Form):
        """Include widget JS and CSS on the page.

        Call this as the last thing before returning template context variables from your view.
        """
        form.resource_registry.pull_in_resources(self.request, form)


class Show(FormView):
    """Show one instance of a model."""

    resource_buttons = [TraverseLinkButton(id="edit", name="Edit", view_name="edit")]

    def get_title(self):
        return "#{}".format(self.get_object().id)

    def get_form(self):
        return self.create_form(EditMode.show, buttons=())

    @view_config(context=Resource, name="show", renderer="crud/show.html", permission='view')
    def show(self):
        """View for showing an individual object."""

        obj = self.context.get_object()
        base_template = self.base_template

        form = self.get_form()
        appstruct = form.schema.dictify(obj)
        rendered_form = form.render(appstruct, readonly=True)

        resource_buttons = self.get_resource_buttons()

        crud = self.get_crud()

        title = current_view_name = self.get_title()

        self.pull_in_widget_resources(form)

        return dict(form=rendered_form, context=self.context, obj=obj, title=title, crud=crud, base_template=base_template, resource_buttons=resource_buttons)


class Edit(FormView):
    """Edit model instance using Deform form..

    The call order of functions

    * ``edit()``

    * ``save_changes()``

    * ``do_success()``
    """

    resource_buttons = [TraverseLinkButton(id="show", name="Show", view_name="show")]

    def get_title(self):
        return "Editing #{}".format(self.get_object().id)

    def get_form(self):
        return self.create_form(EditMode.edit, buttons=("save", "cancel",))

    def bind_schema(self, schema):
        return schema.bind(obj=self.context.get_object(), request=self.request, context=self.context)

    def do_success(self) -> Response:
        """Called after the save (objectify) has succeeded."""
        messages.add(self.request, kind="success", msg="Changes saved.", msg_id="msg-changes-saved")

        # Redirect back to view page after edit page has succeeded
        return HTTPFound(self.request.resource_url(self.context, "show"))

    def do_cancel(self) -> Response:
        """Called when user presses the cancel button.

        :return: HTTPResponse
        """

        # Redirect back to view page after edit page has succeeded
        return HTTPFound(self.request.resource_url(self.context, "show"))

    def save_changes(self, form:deform.Form, appstruct:dict, obj:object):
        """Store the data from the form on the object."""
        form.schema.objectify(appstruct, obj)

    @view_config(context=Resource, name="edit", renderer="crud/edit.html", permission='edit')
    def edit(self):
        """View for showing an individual object."""

        # SQLAlchemy model instance
        obj = self.context.get_object()
        base_template = self.base_template

        # Create form, convert instance to Colander structure for Deform
        form = self.get_form()

        crud = self.get_crud()

        title = current_view_name = self.get_title()

        if "save" in self.request.POST:

            controls = self.request.POST.items()

            try:
                appstruct = form.validate(controls)
                self.save_changes(form, appstruct, obj)
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

        self.pull_in_widget_resources(form)

        return dict(form=rendered_form, context=self.context, obj=obj, title=title, crud=crud, base_template=base_template, resource_buttons=self.get_resource_buttons())


class Add(FormView):
    """Create a new item in CRUD."""

    def get_title(self):
        return "Add new {}".format(self.get_crud().singular_name)

    def get_form(self) -> object:
        return self.create_form(EditMode.add, buttons=("add", "cancel",))

    def get_crud(self) -> CRUD:
        """Get CRUD manager object for this view."""
        return self.context

    def get_model(self) -> type:
        return self.get_crud().get_model()

    def create_object(self):
        """Create new empty object to be populated from the form."""
        model = self.get_model()
        return model()

    def initialize_object(self, form, appstruct: dict, obj: object):
        """Record values from the form on a freshly created object."""
        form.schema.objectify(appstruct, obj)

    def add_object(self, obj):
        """Flush newly created object to persist storage."""
        dbsession = self.context.get_dbsession()
        dbsession.add(obj)
        dbsession.flush()

    def do_success(self, resource: Resource):
        """Finish action after saving new object.

        Usually returns HTTP redirect to the next view.
        """
        messages.add(self.request, kind="success", msg="Item added.", msg_id="msg-item-added")
        # Redirect back to view page after edit page has succeeded
        return HTTPFound(self.request.resource_url(resource, "show"))

    @view_config(context=CRUD, name="add", renderer="crud/add.html", permission='add')
    def add(self):
        """View for showing an individual object."""

        # SQLAlchemy model instance
        base_template = self.base_template

        # Create form, convert instance to Colander structure for Deform
        form = self.get_form()

        crud = self.get_crud()

        title = current_view_name = self.get_title()

        if "add" in self.request.POST:

            controls = self.request.POST.items()

            try:
                appstruct = form.validate(controls)

                # Cannot update id, as it is read-only
                if 'id' in appstruct:
                    del appstruct["id"]

                obj = self.create_object()
                self.initialize_object(form, appstruct, obj)
                # We do not need to explicitly call save() or commit() as we are using Zope transaction manager
                self.add_object(obj)

                resource = crud.wrap_to_resource(obj)

                return self.do_success(resource)

            except deform.ValidationFailure as e:
                # Whoops, bad things happened, render form with validation errors
                rendered_form = e.render()

        elif "cancel" in self.request.POST:
            # User pressed cancel
            return HTTPFound(self.request.resource_url(self.get_crud(), "listing"))
        else:
            # Render initial form view with populated values
            rendered_form = form.render()

        self.pull_in_widget_resources(form)

        return dict(form=rendered_form, context=self.context, title=title, crud=crud, base_template=base_template, resource_buttons=self.get_resource_buttons())


class Delete:
    """Delete one item within a CRUD with a confirmation screen.

    This is an abstract item delete implementation; you must either set :py:attr:`deleter` callback or override :py:meth:`yes`.
    """
    base_template = None

    #: callback ``deleter(request, context)`` which is called to perform the actual model specific delete operation.
    deleter = None

    def __init__(self, context: Resource, request: Request):
        self.context = context
        self.request = request

    def get_crud(self) -> CRUD:
        return self.context.__parent__

    def get_model(self) -> object:
        return self.context.get_model()

    def delete_item(self):
        """User picked YEAH LET'S DO IT."""
        if not self.deleter:
            raise NotImplementedError("The subclass must implement actual delete method or give deleter callback.")

        self.deleter(self.context, self.request)

        messages.add(self.request, "Deleted {}".format(self.context.get_title()), msg_id="msg-item-deleted", kind="success")

        return HTTPFound(self.request.resource_url(self.get_crud(), "listing"))

    def cancel_delete(self):
        """Permanent data destruction is bad.

        Redirect user back to the show view.
        """
        return HTTPFound(self.request.resource_url(self.context, "show"))

    @view_config(context=Resource, name="delete", renderer="crud/delete.html", permission='delete')
    def delete(self):
        """Delete view endpoint."""

        choices = (
            interstitial.Choice("Yes", self.delete_item, id="btn-delete-yes"),
            interstitial.Choice("No", self.cancel_delete, id="btn-delete-no"),
        )

        if self.request.method == "POST":
            return interstitial.process_interstitial(self.request, choices)

        # Expose base_template to the template rendering
        base_template = self.base_template

        return locals()
