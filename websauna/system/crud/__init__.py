"""An abstract CRUD implementation based on traversal. The default support for SQLAlchemy and Deform."""
# Standard Library
import typing as t
from abc import abstractmethod

# Pyramid
from pyramid.interfaces import IRequest

# Websauna
from websauna.system.core.traversal import Resource as _Resource
from websauna.system.http import Request

from .urlmapper import Base64UUIDMapper


class Resource(_Resource):
    """One object in CRUD traversing.

    Maps the raw database object under CRUD view/edit/delete control to traverse path.

    Presents an underlying model instance mapped to an URL path. ``__parent__`` attribute points to a CRUD instance.
    """

    def __init__(self, request: Request, obj: object):
        """Initialize resource object.

        :param obj: The underlying object we wish to wrap for traversing. Usually SQLAlchemy model instance.
        """
        # Some safety checks we get arguments correctly.n
        assert IRequest.providedBy(request)

        self.request = request
        self.obj = obj

    def get_object(self) -> t.Any:
        """Return the wrapped database object."""
        return self.obj

    def get_path(self):
        """Extract the traverse path name from the database object."""
        assert hasattr(self, "__parent__"), "get_path() can be called only for objects whose lineage is set by make_lineage()"

        crud = self.__parent__
        path = crud.mapper.get_path_from_object(self.obj)
        return path

    def get_model(self) -> type:
        """Get the model class represented by this resource."""
        return self.__parent__.get_model()

    def get_title(self) -> str:
        """Title used on view, edit, delete, pages.

        By default use the capitalized URL path path.
        """
        return self.get_path()


class CRUD(_Resource):
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
    title = "(untitled CRUD)"

    # TODO: This is inperfect directly copied from Django - many languages have more plural forms than two. Fix when i18n lands
    #: Helper noun used in the default placeholder texts
    singular_name = "item"

    # TODO: This is inperfect directly copied from Django - many languages have more plural forms than two. Fix when i18n lands
    #: Helper noun used in the default placeholder texts
    plural_name = "items"

    #: Mapper defines how objects are mapped to URL space. The default mapper assumes models have attribute ``uuid`` which is base64 encoded to URL. You can change this to :py:class:`websauna.system.crud.urlmapper.IdMapper` if you instead to want to use ``id`` as a running counter primary column in URLs. This is not recommended in security wise, though.
    mapper = Base64UUIDMapper()

    def make_resource(self, obj: object) -> Resource:
        """Take raw model instance and wrap it to Resource for traversing.

        :param obj: SQLAlchemy object or similar model object.
        :return: :py:class:`websauna.core.traverse.Resource`
        """

        # Use internal Resource class to wrap the object
        if hasattr(self, "Resource"):
            return self.Resource(self.request, obj)

        raise NotImplementedError("Does not know how to wrap to resource: {obj}".format(obj=obj))

    def wrap_to_resource(self, obj: object) -> Resource:
        """Wrap object to a traversable part.

        :param obj: SQLAlchemy object or similar model object.
        :return: :py:class:`websauna.core.traverse.Resource`
        """
        instance = self.make_resource(obj)

        path = self.mapper.get_path_from_object(obj)
        assert type(path) == str, "Object {obj} did not map to URL path correctly, got path {path}".format(obj=obj, path=path)
        instance.make_lineage(self, instance, path)
        return instance

    def traverse_to_object(self, path: str) -> Resource:
        """Wraps object to a traversable URL.

        Loads raw database object with id and puts it inside ``Instance`` object, with ``__parent__`` and ``__name__`` pointers.

        :param path: Path to be traversed to.
        :return: :py:class:`websauna.core.traverse.Resource`
        """
        # First try if we get an view for the current instance with the name
        id = self.mapper.get_id_from_path(path)
        obj = self.fetch_object(id)
        return self.wrap_to_resource(obj)

    @abstractmethod
    def fetch_object(self, id: str) -> object:
        """Load object from the database for CRUD path for view/edit/delete.

        :param id: Object id.
        :return: Object from database.
        """
        raise NotImplementedError('Please use concrete subclass like websauna.syste.crud.sqlalchemy')

    def get_object_url(self, obj: object, view_name: t.Optional[str]=None) -> str:
        """Get URL for view for an object inside this CRUD.

        :param obj: Raw object, e.g. SQLAlchemy instance, which can be wrapped with ``wrap_to_resource``.
        :param view_name: Traverse view name for the resource. E.g. ``show``, ``edit``.
        :return: URL to the object.
        """
        res = self.wrap_to_resource(obj)
        args = [res, ]
        if view_name:
            args.append(view_name)
        return self.request.resource_url(*args)

    def delete_object(self, obj: object):
        """Delete one item in the CRUD.

        Called by delete view if no alternative logic is implemented.
        :param obj: Raw object, e.g. SQLAlchemy instance.
        """
        raise NotImplementedError("The subclass must implement actual delete method or give deleter callback in Delete view.")

    def __getitem__(self, path: str) -> Resource:
        """Traverse to a model instance.

        :param path: Part of URL which is resolved to an object via ``mapper``.
        :return: :py:class:`websauna.core.traverse.Resource`
        """
        if not self.mapper.is_id(path):
            # Signal that this id is not part of the CRUD database and may be a view
            raise KeyError

        return self.traverse_to_object(path)
