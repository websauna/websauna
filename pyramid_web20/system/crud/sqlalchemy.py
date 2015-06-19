from . import CRUD as _CRUD
from . import Resource as _Resource

from pyramid_web20.system.model import DBSession


class Resource(_Resource):
    """Map SQLAlchemy object to a traversable URL path.

    Describe how to display SQLAlchemy objects in breadcrumbs.
    """

    def get_title(self):
        """Title on show / edit / delete pages."""
        return "{} #{}".format(self.__parent__.title, self.obj.id)


class CRUD(_CRUD):
    """CRUD controller utilizing admin interface permissions and templates."""

    def __init__(self, model):
        super(CRUD, self).__init__()
        self.model = model

    def get_model(self):
        return self.model

    def get_query(self):
        """Get SQLAlchemy Query object which we use to populate this listing.

        Views can specify their own queries - e.g. filter by user. This is just the default for everything.
        """
        model = self.get_model()
        return DBSession.query(model)

    def fetch_object(self, id):
        """Pull a raw object from the database.

        Use the ``get_query()`` to get the query base and then return the object with matching id.

        First check for legal ids and raise KeyError to signal that the traversed ``id`` might be actually a view name.
        """
        model = self.get_model()

        column_name = self.mapper.mapping_attribute

        column_instance = getattr(model, column_name, None)
        assert column_instance, "Model {} does not define column/attribute {} used for CRUD resource traversing".format(self.model, column_name)

        obj = self.get_query().filter(column_instance==id).first()
        if not obj:
            raise KeyError("Object id {} was not found for CRUD {} using model {}".format(id, self, model))

        return obj

