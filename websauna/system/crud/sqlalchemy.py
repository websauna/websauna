from pyramid.interfaces import IRequest
from . import CRUD as _CRUD
from . import Resource as _Resource


class Resource(_Resource):
    """Map SQLAlchemy object to a traversable URL path.

    Describe how to display SQLAlchemy objects in breadcrumbs.
    """

    def get_title(self):
        """Title on show / edit / delete pages."""
        return "{} #{}".format(self.__parent__.title, self.obj.id)


class CRUD(_CRUD):
    """CRUD controller utilizing admin interface permissions and templates."""

    def __init__(self, request:IRequest, model:type=None):
        """Create a CRUD root resource for a given model.

        :param model: Can be set on class level or instance level.
        """
        super(CRUD, self).__init__(request)

        if model is not None:
            self.model = model

    def get_model(self):
        """Get the SQLAlchemy model instance we are managing."""
        return self.model

    def get_query(self):
        """Get SQLAlchemy Query object which we use to populate this listing.

        Views can specify their own queries - e.g. filter by user. This is just the default for everything.
        """
        model = self.get_model()
        dbsession = self.request.dbsession
        return dbsession.query(model)

    def fetch_object(self, dbsession, id):
        """Pull a raw object from the database.

        Use the ``get_query()`` to get the query base and then return the object with matching id.

        First check for legal ids and raise KeyError to signal that the traversed ``id`` might be actually a view name.
        """
        model = self.get_model()

        column_name = self.mapper.mapping_attribute

        column_instance = getattr(model, column_name, None)
        assert column_instance, "Model {} does not define column/attribute {} used for CRUD resource traversing".format(self.model, column_name)

        obj = self.get_query(dbsession).filter(column_instance==id).first()
        if not obj:
            raise KeyError("Object id {} was not found for CRUD {} using model {}".format(id, self, model))

        return obj

