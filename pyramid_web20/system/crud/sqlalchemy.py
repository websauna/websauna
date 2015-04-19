from . import CRUD
from . import Listing as _Listing
from . import Instance as _Instance

from pyramid_web20.models import DBSession


class ModelCRUDInstance(_Instance):

    def get_title(self):
        return "{} #{}".format(self.__parent__.friendly_name, self.obj.id)

    def get_id(self):
        return self.obj.id


class ModelCRUD(CRUD):
    """CRUD controller utilizing admin interface permissions and templates."""

    instance = ModelCRUDInstance

    def get_model(self):
        model_admin = self.__parent__
        return model_admin.model

    def get_query(self):
        """Get SQLAlchemy Query object which we use to populate this listing.

        Views can specify their own queries - e.g. filter by user. This is just the default for everything.
        """
        model = self.get_model()
        return DBSession.query(model)

    def fetch_object(self, id):

        model = self.get_model()

        assert type(id) in (int, str), "Got bad id {} ({}) for {}".format(id, type(id), model)

        obj = self.get_query().get(id)
        if not obj:
            raise KeyError("Object id {} was not found for model {}".format(id, model))

        return obj


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
        return self.__parent__.get_query()

    def get_count(self, query):
        return query.count()

