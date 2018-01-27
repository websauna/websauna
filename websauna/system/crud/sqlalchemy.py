"""SQLAlchemy form support."""
# Standard Library
import typing as t

# Pyramid
from pyramid.interfaces import IRequest

# SQLAlchemy
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session

# Websauna
from websauna.system.http import Request

from . import CRUD as _CRUD
from . import Resource as _Resource


class Resource(_Resource):
    """Maps one SQLAlchemy model instance to a traversable URL path.

    Describe how to display SQLAlchemy objects in breadcrumbs.
    """

    def get_title(self):
        """Title on show / edit / delete pages."""
        return "{parent_title} #{id}".format(
            parent_title=self.__parent__.title,
            id=self.obj.id
        )


class CRUD(_CRUD):
    """SQLAlchemy CRUD controller.

    A traversing endpoint which maps listing, add, edit and delete views for an SQLAlchemy model.
    """

    def __init__(self, request: IRequest, model: t.Optional[type]=None):
        """Create a CRUD root resource for a given model.

        :param request: Current HTTP Request.
        :param model: Can be set on class level or instance level.
        """
        super(CRUD, self).__init__(request)

        if model is not None:
            self.model = model

    def get_model(self):
        """Get the SQLAlchemy model instance we are managing.

        :return: SQLAlchemy model instance.
        """
        return self.model

    def get_dbsession(self) -> Session:
        """Override to use a different database session.

        Default to ``request.dbsession``.

        :return: A database session.
        """
        return self.request.dbsession

    def get_query(self) -> Query:
        """Get SQLAlchemy Query object which we use to populate this listing.

        Views can specify their own queries - e.g. filter by user. This is just the default for everything.

        :return: SQLAlchemy query.
        """
        model = self.get_model()
        dbsession = self.get_dbsession()
        return dbsession.query(model)

    def delete_object(self, obj):
        """Delete one item in the CRUD.

        Called by delete view if no alternative logic is implemented.
        :param obj: Raw object, e.g. SQLAlchemy instance.
        """
        dbsession = self.get_dbsession()
        return dbsession.delete(obj)

    def fetch_object(self, id):
        """Pull a raw object from the database.

        Use the ``get_query()`` to get the query base and then return the object with matching id.

        First check for legal ids and raise KeyError to signal that the traversed ``id`` might be actually a view name.
        """
        model = self.get_model()

        column_name = self.mapper.mapping_attribute

        column_instance = getattr(model, column_name, None)
        assert column_instance, "Model {} does not define column/attribute {} used for CRUD resource traversing".format(self.model, column_name)

        obj = self.get_query().filter(column_instance == id).first()
        if not obj:
            raise KeyError("Object id {} was not found for CRUD {} using model {}".format(id, self, model))

        return obj


def sqlalchemy_deleter(view: object, context: Resource, request: Request):
    """A view callback to delete item in SQLAlchemy CRUD.

    :param view: View object.
    :param context: Traversal context
    :param request: Current HTTP Request.
    """
    obj = context.get_object()
    dbsession = request.dbsession
    dbsession.delete(obj)
