from . import CRUD
from . import Listing as _Listing

from pyramid_web20.models import DBSession

class ModelCRUD(CRUD):
    """CRUD controller utilizing admin interface permissions and templates."""

    def get_model(self):
        model_admin = self.__parent__
        return model_admin.model


class ModelCRUDPart:
    """Traversing part.

    __parent__ points to ModelCRUD instance.

    """

    def get_model(self):
        """.Get model from ModelCRUD instance."""
        return self.__parent__.get_model()


class Listing(ModelCRUDPart, _Listing):

    def get_query(self, controller):
        """Get SQLAlchemy Query object which we use to populate this listing.

        Views can specify their own queries - e.g. filter by user. This is just the default for everything.
        """
        model = self.get_model()
        return DBSession.query(model)

    def get_count(self, query):
        return query.count()

