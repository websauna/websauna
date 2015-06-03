
class Table:
    """Describe table columns to a CRUD listing view."""

    def __init__(self, columns=[]):
        self.columns = columns

    def get_columns(self):
        return self.columns


class Column:
    """Define listing in a column."""

    header_template = "crud/column_header.html"

    body_template = "crud/column_body.html"

    navigate_view_name = None

    #: Callback get_navigate_url(request, resource) to resolve the link where the item this column should point to
    navigate_url_getter = None

    getter = None

    #: Arrow formatting string
    format = "MM/DD/YYYY HH:mm"

    def __init__(self, id, name=None, renderer=None, header_template=None, body_template=None, getter=None, format=None, navigate_view_name=None, navigate_url_getter=None):
        """
        :param id: Must match field id on the model
        :param name:
        :param renderer:
        :param header_template:
        :param body_template:
        :param navigate_view_name: If set, make this column clickable and navigates to the traversed name. Options are "show", "edit", "delete"
        :return:
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

    def get_value(self, obj):
        """Extract value from the object for this column.

        Called in listing body.
        """

        if self.getter:
            val = self.getter(obj)
        else:
            val = getattr(obj, self.id)

        if val is None:
            return ""
        else:
            return val

    def get_navigate_target(self, resource, request):
        """Get URL where clicking the link in the listing should go.

        By default, navigate to "show" view of the resource.
        """
        return resource

    def get_navigate_url(self, resource, request, view_name=None):
        """Get the link where clicking this item should take the user.

        By default, navigate to "show" view of the resource.

        TODO: Switch resource/request argument order.

        :param view_name: Override class's ``navigate_view_name``.
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


class ControlsColumn(Column):
    """Render View / Edit / Delete buttons."""
    def __init__(self, id="controls", name="View / Edit", header_template="crud/column_header_controls.html", body_template="crud/column_body_controls.html"):
        super(ControlsColumn, self).__init__(id=id, name=name, header_template=header_template, body_template=body_template)


class FriendlyTimeColumn(Column):
    """Print both accurate time and humanized relative time."""
    def __init__(self, id, name, navigate_view_name=None, timezone=None, header_template=None, body_template="crud/column_body_friendly_time.html"):

        if timezone:
            self.timezone = timezone

        super(FriendlyTimeColumn, self).__init__(id=id, name=name, navigate_view_name=navigate_view_name, header_template=header_template, body_template=body_template)



