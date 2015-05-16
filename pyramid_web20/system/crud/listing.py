
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

    getter = None

    #: Arrow formatting string
    format = "MM/DD/YYYY HH:mm"

    def __init__(self, id, name=None, renderer=None, header_template=None, body_template=None, getter=None, format=None, navigate_view_name=None):
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

    def get_navigate_target(self, resource):
        """Get URL where clicking the link in the listing should go.

        By default, navigate to "show" view of the resource.
        """
        return resource

    def get_navigate_url(self, resource, request, view_name=None):
        """Get the link where clicking this item should take the user.

        By default, navigate to "show" view of the resource.

        :parma view_name: Override class's ``navigate_view_name``.
        """

        target = self.get_navigate_target(resource)

        if not target:
            return None

        view_name = view_name or self.navigate_view_name or "show"

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



