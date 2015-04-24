"""CRUD based on SQLAlchemy and Deform."""
from abc import abstractmethod
from pyramid_web20.utils import traverse

class CRUD(traverse.BreadcrumsResource):
    """Define create-read-update-delete inferface for an model.

    We use Pyramid traversing to get automatic ACL permission support for operations. As long given CRUD resource parts define __acl__ attribute, permissions are respected automatically.

    URLs are the following:

        List: $base/listing

        Add: $parent/add

        View: $parent/$id

        Edit: $parent/$id/edit

        Delete: $parent/$id/delete
    """

    # How the model is referred in templates. e.g. "User"
    title = "xx"

    #: Factory for creating $base/id traversing parts. Maps to the show object.
    instance = None

    #: Listing object presenting $base/listing traversing part. Maps to show view
    listing = None

    show = None
    add = None
    edit = None
    delete = None

    def __init__(self):
        self.init_lineage()

    def init_lineage(self):
        """Set traversing path of hardcoded subresources."""

        # TODO: currently it is not possible to share CRUD parts among the classe. Create factory methods which can be called in the case we want to use the same Listing() across several CRUDs, etc.

        traverse.make_lineage(self, self.listing, "all", allow_reinit=True)
        traverse.make_lineage(self, self.add, "add", allow_reinit=True)


    def get_model(self):
        pass

    def make_instance(self, obj):
        # Wrap object to a traversable part
        instance = self.instance(obj)
        traverse.make_lineage(self, instance, instance.get_id())
        return instance

    def traverse_to_object(self, id):
        """Wraps object to a traversable URL.

        Loads raw database object with id and puts it inside ``Instance`` object,
         with ``__parent__`` and ``__name__`` pointers.
        """
        obj = self.fetch_object(id)
        return self.make_instance(obj)

    def __getitem__(self, id):
        if id == "all":
            return self.listing
        elif id == "add":
            return self.add
        else:
            return self.traverse_to_object(id)

    @abstractmethod
    def fetch_object(self, id):
        """Load object from the database for CRUD path for view/edit/delete."""
        raise NotImplementedError("Please use concrete subclass like pyramid_web20.syste.crud.sqlalchemy")

    def get_breadcrumbs_title(self):
        if self.title:
            return self.title
        return str(self.__class__)

    def order_listing_query(self, query):
        return query


class CRUDResourcePart(traverse.BreadcrumsResource):
    """A resource part of CRUD traversing."""

    template = None

    def get_crud(self):
        return self.__parent__

    def get_model(self):
        return self.__parent__.get_model()


class Instance(traverse.BreadcrumsResource):
    """An object for view, edit, delete screen."""

    template = "crud/show.html"

    def __init__(self, obj):
        self.obj = obj

    @abstractmethod
    def get_id(self):
        """Extract id from the self.obj for traversing."""
        raise NotImplementedError()

    def get_model(self):
        return self.__parent__.get_model()

    def get_title(self):
        """Title used on view, edit, delete, pages."""
        return self.get_id()


class Column:
    """Define listing in a column. """

    header_template = "crud/column_header.html"

    body_template = "crud/column_body.html"

    navigate_to = None

    getter = None

    #: Arrow formatting string
    format = "MM/DD/YYYY HH:mm"

    def __init__(self, id, name=None, renderer=None, header_template=None, body_template=None, getter=None, format=None, navigate_to=None):
        """
        :param id: Must match field id on the model
        :param name:
        :param renderer:
        :param header_template:
        :param body_template:
        :param navigate_to: If set, make this column clickable and navigates to the traversed name. Options are "show", "edit", "delete"
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

        if navigate_to:
            self.navigate_to = navigate_to

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

    def get_navigate_target(self, instance):
        """ """

        if not self.navigate_to:
            return None

        if self.navigate_to == "show":
            return instance
        else:
            return instance[self.navigate_to]

    def get_navigate_url(self, instance, request):
        """Get the link where clicking this item should take the user."""
        target = self.get_navigate_target(instance)
        if not target:
            return None
        return request.resource_url(target)

class ControlsColumn(Column):
    """Render View / Edit / Delete buttons."""
    def __init__(self, id="controls", name="View / Edit", header_template="crud/column_header_controls.html", body_template="crud/column_body_controls.html"):
        super(ControlsColumn, self).__init__(id=id, name=name, header_template=header_template, body_template=body_template)


class FriendlyTimeColumn(Column):
    """Print both accurate time and humanized relative time."""
    def __init__(self, id, name, navigate_to=None, timezone=None, header_template=None, body_template="crud/column_body_friendly_time.html"):

        if timezone:
            self.timezone = timezone

        super(FriendlyTimeColumn, self).__init__(id=id, name=name, navigate_to=navigate_to, header_template=header_template, body_template=body_template)



class CRUDObjectPart:
    """A resource part of CRUD traversing."""

    template = None

    def get_model(self):
        return self.__parent__.get_model()

    def __getitem__(self, item):
        pass


class Listing(CRUDResourcePart):
    """Describe mappings to a CRUD listing view."""

    #: In which frame we embed the listing. The base template must defined {% block crud_content %}
    base_template = None

    title = "All"

    def __init__(self, title=None, columns=[], template=None, base_template=None):

        self.columns = columns

        if title:
            self.title = title

        if template:
            self.template = template

        if base_template:
            self.base_template = base_template

    @abstractmethod
    def get_count(self):
        """Get count of total items of this mode."""
        raise NotImplementedError("Please use concrete subclass like pyramid_web20.syste.crud.sqlalchemy.Listing")

    @abstractmethod
    def get_batch(self, start, end):
        """Get batch of items from start to end."""
        raise NotImplementedError("Please use concrete subclass like pyramid_web20.syste.crud.sqlalchemy.Listing")

    def get_instance(self, obj):
        return self.get_crud().make_instance(obj)

    def get_breadcrumbs_title(self):
        return self.title


class Show:
    """View the item."""

    def __init__(self, includes=None):
        """
        :param includes ``includes`` hint for ``colanderalchemy.SQLAlchemySchemaNode``
        """
        self.includes = includes


