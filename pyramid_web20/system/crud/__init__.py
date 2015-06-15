"""CRUD based on SQLAlchemy and Deform."""
from abc import abstractmethod, abstractproperty
from pyramid_web20.system.core import traverse


from . import mapper


class CRUD(traverse.Resource):
    """Define create-read-update-delete interface for an model.

    We use Pyramid traversing to get automatic ACL permission support for operations. As long given CRUD resource parts define __acl__ attribute, permissions are respected automatically.

    URLs are the following:

        List: $base/listing

        Add: $base/add

        Show $base/$id/show

        Edit: $base/$id/edit

        Delete: $base/$id/delete
    """

    # How the model is referred in templates. e.g. "User"
    title = "xx"

    #: Helper noun used in the default placeholder texts
    singular_name = "item"

    #: Helper noun used in the default placeholder texts
    plural_name = "items"

    #: Mapper defines how objects are mapped to URL space
    mapper = mapper.IdMapper()

    def make_resource(self, obj):
        """Take raw model instance and wrap it to Resource for traversing.

        :param obj: SQLALchemy object or similar model object.
        :return: :py:class:`pyramid_web20.core.traverse.Resource`
        """

        # Use internal Resource class to wrap the object
        if hasattr(self, "Resource"):
            return self.Resource(obj)

        raise NotImplementedError("Does not know how to wrap to resource: {}".format(obj))

    def wrap_to_resource(self, obj):
        # Wrap object to a traversable part
        instance = self.make_resource(obj)

        path = self.mapper.get_path_from_object(obj)
        assert type(path) == str, "Object {} did not map to URL path correctly, got path {}".format(obj, path)
        print(instance, path)
        instance.make_lineage(self, instance, path)
        return instance

    def traverse_to_object(self, path):
        """Wraps object to a traversable URL.

        Loads raw database object with id and puts it inside ``Instance`` object,
         with ``__parent__`` and ``__name__`` pointers.
        """

        # First try if we get an view for the current instance with the name
        id = self.mapper.get_id_from_path(path)
        obj = self.fetch_object(id)
        return self.wrap_to_resource(obj)

    @abstractmethod
    def fetch_object(self, id):
        """Load object from the database for CRUD path for view/edit/delete."""
        raise NotImplementedError("Please use concrete subclass like pyramid_web20.syste.crud.sqlalchemy")

    def get_object_url(self, request, obj, view_name=None):
        """Get URL for view for an object inside this CRUD.

        ;param request: HTTP request instance

        :param obj: Raw object, e.g. SQLAlchemy instance, which can be wrapped with ``wrap_to_resource``.

        :param view_name: Traverse view name for the resource. E.g. ``show``, ``edit``.
        """
        res = self.wrap_to_resource(obj)
        if view_name:
            return request.resource_url(res, view_name)
        else:
            return request.resource_url(res)

    def __getitem__(self, path):

        if self.mapper.is_id(path):
            return self.traverse_to_object(path)
        else:
            # Signal that this id is not part of the CRUD database and may be a view
            raise KeyError


class Resource(traverse.Resource):
    """One object in CRUD traversing.

    Maps the raw database object under CRUD view/edit/delete control to traverse path.

    Presents an underlying model instance mapped to an URL path. ``__parent__`` attribute points to a CRUD instance.
    """

    def __init__(self, obj):
        self.obj = obj

    def get_object(self):
        """Return the wrapped database object."""
        return self.obj

    def get_path(self):
        """Extract the traverse path name from the database object."""
        assert hasattr(self, "__parent__"),  "get_path() can be called only for objects whose lineage is set by make_lineage()"

        crud = self.__parent__
        path = crud.mapper.get_path_from_object(self.obj)
        return path

    def get_model(self):
        return self.__parent__.get_model()

    def get_title(self):
        """Title used on view, edit, delete, pages.

        By default use the capitalized URL path path.
        """
        return self.get_path()

