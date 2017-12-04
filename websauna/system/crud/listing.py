"""Listing views."""
# Standard Library
import typing as t

# Websauna
from websauna.system.http import Request

from . import Resource


class Column:
    """Define a column in a listing."""

    header_template = "crud/column_header.html"
    body_template = "crud/column_body.html"
    navigate_view_name = None

    #: Callback get_navigate_url(request, resource) to resolve the link where the item this column should point to
    navigate_url_getter = None
    getter = None

    #: Arrow formatting string
    format = "MM/DD/YYYY HH:mm"

    def __init__(
            self,
            id: str,
            name: t.Optional[str]=None,
            renderer=None,
            header_template: t.Optional[str]=None,
            body_template: t.Optional[str]=None,
            getter: t.Optional[t.Callable]=None,
            format: t.Optional[str]=None,
            navigate_view_name=None, navigate_url_getter=None):
        """Initialize Column.

        :param id: Column id. Must match field id on the model
        :param name: Column name, to be displayed on the header of the table.
        :param renderer:
        :param header_template: Path to header template to be used.
        :param body_template: Path to body template to be used.
        :param getter: func(view instance, object) - extract value for this column for an object
        :param format: Format to be applied to the value. i.e: "MM/DD/YYYY HH:mm" for a date value.
        :param navigate_url_getter: callback(request, resource) to generate the target URL if the contents of this cell is clicked
        :param navigate_view_name: If set, make this column clickable and navigates to the traversed name. Options are "show", "edit", "delete"
        """
        self.id = id
        self.name = name
        self.renderer = renderer
        self.getter = getter

        if format:
            self.format = format
        if header_template:
            self.header_template = header_template
        if body_template:
            self.body_template = body_template
        if navigate_view_name:
            self.navigate_view_name = navigate_view_name
        if navigate_url_getter:
            self.navigate_url_getter = navigate_url_getter

    def get_value(self, view: t.Any, obj: t.Any):
        """Extract value from the object for this column.

        Called in listing body.

        :param view: View class calling us
        :param obj: The object the list is iterating. Usually an SQLAlchemy model instance.
        """
        if self.getter:
            val = self.getter(view, self, obj)
        else:
            val = getattr(obj, self.id)

        if val is None:
            val = ''
        return val

    def get_navigate_target(self, resource: Resource, request: Request):
        """Get URL where clicking the link in the listing should go.

        By default, navigate to "show" view of the resource.

        :param resource: Traversal context
        :param request: Current HTTP Request.
        """
        return resource

    def get_navigate_url(self, resource: Resource, request: Request, view_name: t.Optional[str]=None):
        """Get the link where clicking this item should take the user.

        By default, navigate to "show" view of the resource.

        TODO: Switch resource/request argument order.
        :param resource: Traversal context
        :param request: Current HTTP Request.
        :param view_name: Override class' ``navigate_view_name``.
        """
        if self.navigate_url_getter:
            return self.navigate_url_getter(request, resource)

        if not self.navigate_view_name:
            return None

        target = self.get_navigate_target(resource, request)

        if not target:
            return None

        view_name = view_name or self.navigate_view_name

        return request.resource_url(target)


class StringPresentationColumn(Column):
    """Renders the default string presentation of the object.

    You can change the stringify method::

        StringPresentationColumn(formatter=my_func)

    where my_func is callable::

        my_func(value)
    """

    def __init__(self, **kwargs):
        """Initialize StringPresentationColumn. """
        self.formatter = kwargs.pop('formatter', str)
        super(StringPresentationColumn, self).__init__(**kwargs)

    def get_value(self, view, obj):
        """Extract value from the object for this column.

        Called in listing body.
        """
        val = str(obj)
        return self.formatter(val)


class ControlsColumn(Column):
    """Render View / Edit / Delete buttons."""

    def __init__(
            self,
            id: str='controls',
            name: t.Optional[str]='Actions',
            header_template: t.Optional[str]='crud/column_header_controls.html',
            body_template: t.Optional[str]='crud/column_body_controls.html'
    ):
        """Initialize ControlsColumn.

        :param id: ID of the column.
        :param name: Column name, to be displayed on the header of the table.
        :param header_template: Path to header template to be used.
        :param body_template: Path to body template to be used.
        """
        super(ControlsColumn, self).__init__(id=id, name=name, header_template=header_template, body_template=body_template)


class FriendlyTimeColumn(Column):
    """Print both accurate time and humanized relative time."""

    def __init__(
            self,
            id: str,
            name: str,
            navigate_view_name: t.Optional[str]=None,
            timezone: t.Optional[str]=None,
            header_template: t.Optional[str]=None,
            body_template: t.Optional[str]='crud/column_body_friendly_time.html'
    ):
        """Initialize FriendlyTimeColumn.

        :param id: Column id. Must match field id on the model
        :param name: Column name, to be displayed on the header of the table.
        :param navigate_view_name: If set, make this column clickable and navigates to the traversed name. Options are "show", "edit", "delete"
        :param timezone: Timezone to be used.
        :param header_template: Path to header template to be used.
        :param body_template: Path to body template to be used.
        """
        if timezone:
            self.timezone = timezone

        super(FriendlyTimeColumn, self).__init__(id=id, name=name, navigate_view_name=navigate_view_name, header_template=header_template, body_template=body_template)


class Table:
    """Describe table columns to a CRUD listing view."""

    def __init__(self, columns: t.Optional[t.List[Column]]=None):
        """Initialize Table.

        :param columns: List of columns to be used to render the list view.
        """
        self.columns = columns or []

    def get_columns(self) -> t.List[Column]:
        """Return columns.

        :return: List of columns to be used to render the list view.
        """
        return self.columns
