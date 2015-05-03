from . import CRUD
from . import Resource as _Resource

from pyramid_web20.models import DBSession


class Resource(_Resource):
    """Map SQLAlchemy object to a traversable URL path.

    Describe how to display SQLAlchemy objects in breadcrumbs.
    """

    def get_title(self):
        """Title on show / edit / delete pages."""
        return "{} #{}".format(self.__parent__.title, self.obj.id)

    def get_id(self):
        return self.obj.id


class ModelCRUD(CRUD):
    """CRUD controller utilizing admin interface permissions and templates."""

    def __init__(self, model):
        super(ModelCRUD, self).__init__()
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
        """Pull a raw SQLAlchemy object from the database.

        Use the ``get_query()`` to get the query base and then return the object with matching id.

        First check for legal ids and raise KeyError to signal that the traversed ``id`` might be actually a view name.
        """
        model = self.get_model()

        try:
            id = int(id)
        except ValueError:
            # For now, we assume that all object travesing ids are integer primary keys.
            # Subclass may want to change this behavior e.g. to have UUID traversing.
            raise KeyError("Cannot traverse {}".format(id))

        obj = self.get_query().filter_by(id=id).first()
        if not obj:
            raise KeyError("Object id {} was not found for model {}".format(id, model))

        return obj