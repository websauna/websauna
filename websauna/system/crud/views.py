"""Default CRUD views."""
# Standard Library
import csv
import re
import typing as t
from abc import abstractmethod
from io import StringIO

# Pyramid
import colander
import deform
import transaction
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

# SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query

from slugify import slugify

# Websauna
from websauna.system.core import messages
from websauna.system.form import interstitial
from websauna.system.form.fieldmapper import EditMode
from websauna.system.form.resourceregistry import ResourceRegistry
from websauna.system.user.models import User

from . import CRUD
from . import Resource
from . import paginator


class ResourceButton:
    """Present a button on the top right corner of CRUD views.

    These buttons, with breadcrumbs, form the basic navigation inside the CRUD management interface.

    Buttons are permission-aware, so they are rendered only when the user has required permission.

    The default button templates include

    * :ref:`template-crud/resource_button.html`

    * :ref:`template-crud/form_button.html`
    """

    #: The template used to render this button. Also overridable through the constructor.
    template = "crud/resource_button.html"

    def __init__(self, id: t.Optional[str]=None, name: t.Optional[str]=None, template: t.Optional[str]=None, permission: t.Optional[str]=None, tooltip: t.Optional[str]=None, feature: t.Optional[str]=None):
        """
        :param id: Id of the button to be used as HTML id
        :param name:  Human readable label of the button
        :param template: Override template for this button
        :param permission: You need to have named permission on the context to make this button visible. Set to none to make the button appear always.
        :param feature: The registry.features set must contain this feature enabled in order for the item to appear
        """

        assert id, "Button id missing"
        assert name, "Button name missing"

        self.id = id
        self.name = name

        self.permission = permission
        self.feature = feature
        self.tooltip = tooltip

        if template:
            self.template = template

    def is_visible(self, context: Resource, request: Request) -> bool:
        """Determine if we should render this button.

        :param context: Traversal context
        :param request: Current HTTP Request.
        :returns: Boolean indicating if button is visible or not.
        """
        visible = True
        if self.permission is not None:
            if not request.has_permission(self.permission, context):
                visible = False

        if self.feature is not None:
            if self.feature not in request.registry.features:
                visible = False

        return visible

    def get_link(self, context: Resource, request: Request) -> str:
        """Generate a link where this button is pointing at.

        :param context: Traversal context
        :param request: Current HTTP Request.
        :returns: Link.
        """
        return "#"

    def render(self, context: Resource, request: Request) -> str:
        """Return HTML code for this button.

        :param context: Traversal context
        :param request: Current HTTP Request.
        :returns: Rendered template.
        """
        template_context = dict(context=context, button=self)
        return render(self.template, template_context, request=request)


class TraverseLinkButton(ResourceButton):
    """A button which is a link to another page on this resource."""

    def __init__(self, view_name: str, **kwargs):
        """
        :param view_name: request.resource_url() view name where this button points at
        :param kwargs: Other ResourceButton construction arguments
        """
        super(TraverseLinkButton, self).__init__(**kwargs)
        self.view_name = view_name

    def get_link(self, context: Resource, request: Request) -> str:
        """Generate a link where this button is pointing at.

        :param context: Traversal context
        :param request: Current HTTP Request.
        :returns: Link.
        """
        return request.resource_url(context, self.view_name)


class CRUDView:
    """Base class for different CRUD views.

    This includes views having context as the listing and having context as the individual item."""

    #: base_template may point into a template providing ``crud_content`` block where the contents of the view is rendered. This allows you to decorate your CRUD which a specific page frame.
    base_template = "crud/base.html"

    #: Instance of ResourceButtons which appear on the top right corner of this view
    resource_buttons = []

    def get_resource_buttons(self) -> t.List:
        """Get the context-sensitive button options presented on this page.

        These are usually links to "Show", "Edit", "Delete" of the formm context, but you are free to add your own buttons here. The buttons are usually placed on the top right corner of the form.

        Unless you want to dynamically generate buttons depending on the page, it is enough to set ``resource_buttons`` attribute on the view class.

        :return: OrderedDict instance where key is button id and value is the link to where the button points.
        """
        return self.resource_buttons


class Listing(CRUDView):
    """List items in CRUD."""

    #: Describe what columns our listing should contain
    table = None  # type: Table

    #: How the result of this list should be split to pages
    paginator = paginator.DefaultPaginator()

    resource_buttons = [TraverseLinkButton(id="add", name="Add", view_name="add", permission="add")]

    def __init__(self, context: CRUD, request: Request):
        """Initialize Listing view.

        :param context: Points to ``CRUD`` instance.
        :param request: Current HTTP Request.
        """
        self.context = context
        self.request = request

    def get_crud(self) -> CRUD:
        return self.context

    def get_model(self) -> t.Any:
        return self.context.get_model()

    def get_query(self) -> Query:
        """Get SQLAlchemy query used in this CRUD listing.

        This can include filtering e.g. request user, crud parameters, so on.
        """
        return self.context.get_query()

    def get_count(self, query: Query):
        """Calculate total item count based on query."""
        return query.count()

    def order_query(self, query: Query):
        """Sort the query."""
        return query

    def get_title(self) -> str:
        """Get the user-readable name of the listing view (breadcrumbs, etc.)"""
        return "All {}".format(self.get_crud().plural_name)

    def paginate(self, template_context):
        """Create template variables for paginatoin results."""
        batch = self.paginator.paginate(
            template_context["query"],
            self.request,
            template_context["count"]
        )
        template_context["batch"] = batch

    @view_config(context=CRUD, name="listing", renderer="crud/listing.html", permission="view")
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
        current_view_name = self.get_title()

        title = self.get_title()
        count = self.get_count(query)

        # Base listing template variables
        template_context = {
            "title": title,
            "current_view_name": current_view_name,
            "query": query,
            "count": count,
            "crud": crud,
            "columns": columns,
            "resource_buttons": self.get_resource_buttons(),
            "base_template": base_template,
            "view": self,
        }

        # Include pagination template context
        self.paginate(template_context)

        return template_context


class CSVListing(Listing):
    """A listing view that exports the listing table as CSV.

    CSVListing users the same :py:class:`Table` structure to define the listing as the listing HTML page. For columns, we use only id and :py:meth:`websauna.system.crud.listing.Column.get_value` to stringify entries from SQLAlchemy model attributes to CSV writer stream.

    For example usage see :py:class:`websauna.system.user.adminviews.UserCSVListing`.

    .. note ::

        This is TODO, having pyramid_tm issue open https://github.com/Pylons/pyramid_tm/issues/56

    Original implementation in https://github.com/nandoflorestan/bag/blob/master/bag/spreadsheet/csv.py by Nando Florestan.
    """

    #: How many rows we buffer in a chunk before writing into a response
    buffered_rows = 100

    @view_config(context=CRUD, name="csv-export", permission='view')
    def listing(self):
        """Listing core."""

        table = self.table
        columns = table.get_columns()
        query = self.get_query()
        query = self.order_query(query)

        file_title = slugify(self.context.title)
        encoding = "utf-8"

        response = Response()
        response.headers["Content-Type"] = "text/csv; charset={}".format(encoding)
        response.headers["Content-Disposition"] = "attachment;filename={filename}.{encoding}.csv".format(
            filename=file_title,
            encoding=encoding
        )

        buf = StringIO()
        writer = csv.writer(buf)
        view = self

        def generate_csv_data():

            # Write headers
            writer.writerow([c.id for c in columns])

            # Write each listing item
            for idx, model_instance in enumerate(query):

                # Extract column values for this row
                values = [c.get_value(view, model_instance) for c in columns]

                writer.writerow(values)
                # if idx % buffered_rows == 0:
                #    yield buf.getvalue().encode(encoding)
                #    buf.truncate(0)  # But in Python 3, truncate() does not move
                #    buf.seek(0)  # the file pointer, so we seek(0) explicitly.

            # yield buf.getvalue().encode(encoding)

            # Abort the transaction, otherwise it might not be closed by underlying machinery
            # (at least tests hang)
            # TODO: Confirm this behavior with pyramid_tm 2.0 when it's out
            # request.tm.abort()

        # TODO: This use to be response.app_iter, but apparently it doesn't place nicely with pyramid_tm
        generate_csv_data()
        response.body = buf.getvalue().encode(encoding)
        return response


class FormView(CRUDView):
    """An abstract base class for form-based CRUD views.

    Use Deform form library. This views is abstract and it does not have dependency to any underlying model system like SQLAlchemy.
    """
    #: If the child class is not overriding the rendering loop, point this to a template which provides the page frame and ``crud_content`` block. For example use see :py:class:`websauna.system.user.adminviews.UserAdd`.
    base_template = "crud/base.html"

    #: This is an instance of :py:class:`websauna.system.crud.formgenerator.FormGenerator`. For SQLAlchemy models it is :py:class:`websauna.system.crud.formgenerator.SQLAlchemyFormGenerator`. Form generator describers how a CRUD model is turned to a Deform form. It is called by :py:meth:`create_form`. For example use cases see e.g. :py:class:`websauna.system.user.adminviews.UserAdd`.
    form_generator = None

    def __init__(self, context: Resource, request: Request):
        """
        :param context: Instance of ``traverse.Resource()`` or its subclasses
        :param request: HTTP request
        """
        self.context = context
        self.request = request

    def create_form(self, mode: EditMode, buttons=(), nested=None) -> deform.Form:
        model = self.get_model()
        assert getattr(self, "form_generator", None), "Class {} must define a form_generator".format(self)
        return self.form_generator.generate_form(request=self.request, context=self.context, model=model, mode=mode, buttons=buttons)

    @abstractmethod
    def get_form(self) -> deform.Form:
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

    def customize_schema(self, schema: colander.Schema):
        """After Colander schema is automatically generated from the SQLAlchemy model, edit it in-place for fine-tuning.

        Override this in your view subclass for schema customizations.
        """
        pass

    def pull_in_widget_resources(self, form: deform.Form):
        """Include widget JS and CSS on the page.

        Call this as the last thing before returning template context variables from your view.
        """

        resource_registry = form.resource_registry
        assert isinstance(resource_registry, ResourceRegistry), "Websauna CRUD view got vanilla deform ResourceRegistry instance. To use widgets with dynamic JavaScript correctly you need to make sure you initialize websauna.system.form.resourceregistry.ResourceRegistry for your form object."

        resource_registry.pull_in_resources(self.request, form)

    def _cleanup_integrity_error(self, form: deform.Form, model: type,
                                 obj_id: t.Any, user_id: t.Any,
                                 error: IntegrityError) -> (t.Any, User):
        """After form data conflicts with data already on the DB,
        inspect the sqlalchemy error, pinpoint the responsible field,
        and prepare the deform.field to raise a meaninful validation error
        on that point.

        Resuming clean request execution requires refetching all
        objects that will be further needed from the DB.
        """
        # Things went as bad as they could.
        # Let's rolback some steps and simulate a validation
        # error in the problematic field, before reshowing the form.

        # Find out field that errored from SQLAlchemy error msg.
        integrity_error_msg = error._message().split("DETAIL: ")[-1].strip()
        key = re.findall(r"\((.*?)\)", integrity_error_msg)[0]
        for schema in form.children:
            if schema.name == key:
                schema_node = schema.schema
                break
        else:
            # field not found
            schema_node = form.schema

        def validator(*args, **kw):
            # TODO: How to actually get an actual translated message?
            # Maybe force user to feed value from his app?
            raise colander.Invalid(schema_node, msg='Value already exists.')
        schema_node.validator = validator

        transaction.abort()

        # Objects are dettached - need to re-fetch a fresh copy
        # from the DB or things will get ugly.

        if obj_id is not None:
            obj = self.request.dbsession.query(model).filter_by(id=obj_id).first()
        else:
            obj = None
        user = self.request.dbsession.query(User).filter_by(id=user_id).first()

        return obj, user


class Show(FormView):
    """Show one instance of a model."""

    resource_buttons = [TraverseLinkButton(id="edit", name="Edit", view_name="edit", permission="edit")]

    def get_title(self):
        return self.context.get_title()

    def get_form(self):
        return self.create_form(EditMode.show, buttons=())

    def get_form_context(self) -> object:
        """Get the item that populates the form."""
        return self.context.get_object()

    def get_appstruct(self, form, form_context) -> dict:
        """Get the dictionary that populates the form."""
        return form.schema.dictify(form_context)

    @view_config(context=Resource, name="show", renderer="crud/show.html", permission='view')
    def show(self):
        """View for showing an individual object."""
        obj = self.get_object()
        form_context = self.get_form_context()
        base_template = self.base_template

        form = self.get_form()
        appstruct = self.get_appstruct(form, form_context)
        rendered_form = form.render(appstruct, readonly=True)

        resource_buttons = self.get_resource_buttons()

        crud = self.get_crud()

        title = self.get_title()
        self.pull_in_widget_resources(form)
        return dict(form=rendered_form, context=self.context, obj=obj, title=title, crud=crud, base_template=base_template, resource_buttons=resource_buttons)


class Edit(FormView):
    """Edit model instance using Deform form..

    The call order of functions

    * ``edit()``

    * ``save_changes()``

    * ``do_success()``
    """

    resource_buttons = [TraverseLinkButton(id="show", name="Show", view_name="show", permission="view")]

    def get_title(self):
        return "Editing #{}".format(self.context.get_title())

    def get_buttons(self) -> t.Iterable[deform.form.Button]:
        return (
            deform.form.Button("save"),
            deform.form.Button("cancel"),
        )

    def get_form(self) -> deform.form.Form:
        """Get a form used to edit this item."""
        return self.create_form(EditMode.edit, buttons=self.get_buttons())

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

    def save_changes(self, form: deform.Form, appstruct: dict, obj: object):
        """Store the data from the form on the object."""
        form.schema.objectify(appstruct, obj)

    def get_appstruct(self, form: deform.Form, obj: object) -> dict:
        """Turn the object to form editable format."""
        return form.schema.dictify(obj)

    @view_config(context=Resource, name="edit", renderer="crud/edit.html", permission='edit')
    def edit(self):
        """View for showing an individual object."""

        # SQLAlchemy model instance
        obj = self.context.get_object()
        base_template = self.base_template

        # Create form, convert instance to Colander structure for Deform
        form = self.get_form()

        crud = self.get_crud()

        title = self.get_title()

        if "save" in self.request.POST:

            controls = self.request.POST.items()

            try:
                controls = list(controls)
                appstruct = form.validate(controls)

                # import colander
                obj_id = obj.id
                user_id = self.request.user.id
                try:
                    self.save_changes(form, appstruct, obj)
                except IntegrityError as error:

                    obj, user = self._cleanup_integrity_error(form, type(obj), obj_id, user_id, error)

                    self.context.obj = obj
                    self.request.user = user

                    # Force raising a deform.ValidatinFailure, triggering
                    # data fill in at the apropriate structures
                    form.validate(controls)

                else:
                    return self.do_success()

            except deform.ValidationFailure as e:
                # Whoops, bad things happened, render form with validation errors
                rendered_form = e.render()

        elif "cancel" in self.request.POST:
            # User pressed cancel
            return self.do_cancel()
        else:
            # Render initial form view with populated values
            appstruct = self.get_appstruct(form, obj)
            rendered_form = form.render(appstruct)

        self.pull_in_widget_resources(form)

        return dict(form=rendered_form, context=self.context, obj=obj, title=title, crud=crud, base_template=base_template, resource_buttons=self.get_resource_buttons(), current_view_name="Edit")


class Add(FormView):
    """Create a new item in CRUD."""

    def get_title(self):
        return "Add new {}".format(self.get_crud().singular_name)

    def get_form(self) -> object:
        return self.create_form(EditMode.add, buttons=self.get_buttons())

    def get_crud(self) -> CRUD:
        """Get CRUD manager object for this view."""
        return self.context

    def get_model(self) -> type:
        return self.get_crud().get_model()

    def create_object(self):
        """Factory method to create a new empty object to be populated from the form."""
        model = self.get_model()
        return model()

    def initialize_object(self, form, appstruct: dict, obj: object):
        """Record values from the form on a freshly created object."""
        form.schema.objectify(appstruct, obj)

    def bind_schema(self, schema):
        return schema.bind(request=self.request, context=self.context)

    def add_object(self, obj):
        """Add objects to transaction lifecycle and flush newly created object to persist storage to give them id."""
        dbsession = self.context.get_dbsession()
        dbsession.add(obj)
        dbsession.flush()

    def do_success(self, resource: Resource) -> Response:
        """Finish action after saving new object.

        Usually returns HTTP redirect to the next view.
        """
        messages.add(self.request, kind="success", msg="Item added.", msg_id="msg-item-added")
        # Redirect back to view page after edit page has succeeded
        return HTTPFound(self.request.resource_url(resource, "show"))

    def do_cancel(self) -> Response:
        """Called when user presses the cancel button.

        :return: HTTPResponse
        """
        return HTTPFound(self.request.resource_url(self.get_crud(), "listing"))

    def build_object(self, form, appstruct: dict) -> object:
        """Builds a new object.

        The default behavior is to call :py:meth:`create_object` to construct a new object, then populate it with :py:meth:`initialize_object` and finally include the created object in the transaction lifecycle with :py:meth:`add_object`.
        """
        obj = self.create_object()
        self.initialize_object(form, appstruct, obj)
        # We do not need to explicitly call save() or commit() as we are using Zope transaction manager
        self.add_object(obj)
        return obj

    def get_buttons(self)-> t.List[deform.form.Button]:
        buttons = (
            deform.form.Button("add"),
            deform.form.Button("cancel"),
        )
        return buttons

    @view_config(context=CRUD, name="add", renderer="crud/add.html", permission='add')
    def add(self):
        """View for showing an individual object."""

        # SQLAlchemy model instance
        base_template = self.base_template

        # Create form, convert instance to Colander structure for Deform
        form = self.get_form()

        crud = self.get_crud()

        title = self.get_title()

        if "add" in self.request.POST:

            controls = self.request.POST.items()

            try:
                controls = list(controls)
                appstruct = form.validate(controls)

                # Cannot update id, as it is read-only
                if 'id' in appstruct:
                    del appstruct["id"]

                user_id = self.request.user.id
                try:
                    obj = self.build_object(form, appstruct)
                    resource = crud.wrap_to_resource(obj)
                except IntegrityError as error:
                    obj, user = self._cleanup_integrity_error(form, self.get_model(), None, user_id, error)

                    self.request.user = user

                    # Force raising a deform.ValidatinFailure, triggering
                    # data fill in at the apropriate structures
                    form.validate(controls)

                return self.do_success(resource)

            except deform.ValidationFailure as e:
                # Whoops, bad things happened, render form with validation errors
                rendered_form = e.render()

        elif "cancel" in self.request.POST:
            # User pressed cancel
            return self.do_cancel()
        else:
            # Render initial form view with populated values
            rendered_form = form.render()

        self.pull_in_widget_resources(form)

        return dict(form=rendered_form, context=self.context, title=title, crud=crud, base_template=base_template, resource_buttons=self.get_resource_buttons(), current_view_name="Add")


class Delete:
    """Delete one item within a CRUD with a confirmation screen.

    This is an abstract item delete implementation; you must either set :py:attr:`deleter` callback or override :py:meth:`yes`.
    """
    base_template = "crud/base.html"

    #: callback ``deleter(request, context)`` which is called to perform the actual model specific delete operation.
    deleter = None

    def __init__(self, context: Resource, request: Request):
        self.context = context
        self.request = request

    def get_crud(self) -> CRUD:
        return self.context.__parent__

    def get_model(self) -> object:
        return self.context.get_model()

    def get_object(self):
        """Get underlying SQLAlchemy model instance from current Pyramid traversing context."""
        return self.context.get_object()

    def delete_object(self):
        """User picked YEAH LET'S DO IT.

        First try to call ``delete`` callback if one is set. If not then fallback to :py:meth:`websauna.system.crud.CRUD.delete_object`.

        http://opensourcehacker.com/wp-content/uploads/2013/04/koala.gif
        """

        if self.deleter:
            self.deleter(self.context, self.request)
        else:
            self.get_crud().delete_object(self.get_object())

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
            interstitial.Choice("Yes", self.delete_object, id="btn-delete-yes"),
            interstitial.Choice("No", self.cancel_delete, id="btn-delete-no"),
        )

        if self.request.method == "POST":
            return interstitial.process_interstitial(self.request, choices)

        # Expose base_template to the template rendering
        base_template = self.base_template

        current_view_name = "Confirm delete"

        return locals()
