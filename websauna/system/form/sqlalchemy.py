"""SQLAlchemy integration for Colander and Deform frameworks."""
# Standard Library
import typing as t

# Pyramid
import colander
from colander.compat import is_nonstr_iter

# SQLAlchemy
from sqlalchemy import Column
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session

# Websauna
from websauna.utils.slug import slug_to_uuid
from websauna.utils.slug import uuid_to_slug


def extract_uuid_to_slug(item):
    """Reads uuid attribute on the model name returns it as B64 encoded slug."""
    return uuid_to_slug(item.uuid)


def convert_query_to_tuples(query: Query, first_column: t.Union[str, t.Callable], second_column: t.Union[str, t.Callable], default_choice: t.Optional[str] =None) -> t.List[t.Tuple[str, str]]:
    """Convert SQLAlchemy query results to (id, name) tuples for select and checkbox widgets.

    :param first_column: Column name used to populate value in the first tuple
    :param second_column: Column name used to populate value in the second tuple
    :oaram default_choice: If given use this as "Select here" or when the value is None
    """
    if type(first_column) == str:
        first_column_getter = lambda item: getattr(item, first_column)
    else:
        first_column_getter = first_column

    if type(second_column) == str:
        second_column_getter = lambda item: getattr(item, second_column)
    else:
        second_column_getter = second_column

    result = []

    if default_choice:
        result.append(('', default_choice))

    for item in query:
        result.append((first_column_getter(item), second_column_getter(item)))

    return result


def get_uuid_vocabulary_for_model(dbsession: Session, model: type, first_column=extract_uuid_to_slug, second_column=str, default_choice=None) -> t.List[t.Tuple]:
    """Create a select/checkbox vocabulary containing all items of a model."""
    query = dbsession.query(model).all()
    return convert_query_to_tuples(query, first_column, second_column, default_choice)


class ModelSetResultList(list):
    """Mark that the result is through SQLAlchemy query."""


class ModelSchemaType:
    """Mixin class for using SQLAlchemy with Colander types.

    Provide utilitiy functions to extract model and dbsession from the context.
    """

    #: Point this to the model this set is supposed to query
    model = None

    #: Name of the column on the model we use to fetch objects using IN query
    match_column = None

    #: Name of the column which provides label or such for items in sequence. If not present item __str__ is used.
    label_column = None

    def __init__(self, model: type=None):
        if model:
            self.model = model

    def get_dbsession(self, node) -> Session:
        return node.bindings["request"].dbsession

    def get_model(self, node) -> type:
        """Which model we are quering."""
        return self.model

    def convert_to_id(self, item):
        id = getattr(item, self.match_column)
        value = getattr(item, self.label_column)
        return (id, value)

    def get_match_column(self, node: colander.SchemaNode, model: type) -> Column:
        """Get the column we are filtering out."""
        assert self.match_column, "match_column undefined"
        return getattr(model, self.match_column)


class ForeignKeyValue(ModelSchemaType, colander.String):
    """Hold a reference to one SQLAlchemy object for Colander schema serialization.

    See :ref:`Widgets <deform:widget>` for more information.
    """

    def serialize(self, node, appstruct):

        if appstruct is colander.null:
            return colander.null

        value = self.preprocess_appstruct_value(node, appstruct)
        return value

    def preprocess_cstruct_value(self, node: colander.SchemaNode, cstruct: set) -> t.Union[set, t.List]:
        """Parse incoming form values to Python objects if needed.
        """
        return cstruct

    def preprocess_appstruct_value(self, node: colander.SchemaNode, appstruct: set) -> t.List[str]:
        """Convert items to appstruct ids.
        """
        return str(appstruct)

    def query_item(self, node: colander.SchemaNode, dbsession: Session, model: type, match_column: Column, value: set) -> t.List[object]:
        """Query the actual model to get the concrete SQLAlchemy objects."""

        if not value:
            # Empty IN queries are not allowed
            return value

        return dbsession.query(model).filter(match_column == value).first()

    def deserialize(self, node, cstruct: str):
        """Convert incoming form value - string id - back to a SQLAlchemy object."""
        if cstruct is colander.null:
            return colander.null

        dbsession = self.get_dbsession(node)
        model = self.get_model(node)
        match_column = self.get_match_column(node, model)
        value = self.preprocess_cstruct_value(node, cstruct)
        value = self.query_item(node, dbsession, model, match_column, value)

        return value


class ModelSet(ModelSchemaType, colander.Set):
    """Presents set of chosen SQLAlchemy models instances.

    This automatically turns SQLAlchemy objects to (id, label) tuples, so that they can be referred in various widgets (select, checkbox).

    See :ref:`Widgets <deform:widget>` for more information.
    """

    def serialize(self, node, appstruct):

        assert self.match_column, "match_column not configured"

        if appstruct is colander.null:
            return colander.null

        values = self.preprocess_appstruct_values(node, appstruct)
        return values

    def deserialize_set_to_models(self, node, cstruct):
        dbsession = self.get_dbsession(node)
        model = self.get_model(node)
        match_column = self.get_match_column(node, model)
        values = self.preprocess_cstruct_values(node, cstruct)
        return self.query_items(node, dbsession, model, match_column, values)

    def preprocess_cstruct_values(self, node: colander.SchemaNode, cstruct: set) -> t.Union[set, t.List]:
        """Parse incoming form values to Python objects if needed.
        """
        return cstruct

    def preprocess_appstruct_values(self, node: colander.SchemaNode, appstruct: set) -> t.List[str]:
        """Convert items to appstruct ids.
        """
        if self.label_column:
            return [getattr(i, self.label_column) for i in appstruct]
        else:
            return [str(i) for i in appstruct]

    def query_items(self, node: colander.SchemaNode, dbsession: Session, model: type, match_column: Column, values: set) -> t.List[object]:
        """Query the actual model to get the concrete SQLAlchemy objects."""
        if not values:
            # Empty IN queries are not allowed
            return []
        return ModelSetResultList(dbsession.query(model).filter(match_column.in_(values)).all())

    def deserialize(self, node, cstruct):

        if cstruct is colander.null:
            return colander.null

        if not is_nonstr_iter(cstruct):
            raise colander.Invalid(node, '{} is not iterable'.format(cstruct))

        return self.deserialize_set_to_models(node, cstruct)


class UUIDForeignKeyValue(ForeignKeyValue):
    """Hold a reference to SQLAlchemy object through base64 encoded UUID value.

    Useful for select widget, etc.

    See :ref:`Widgets <deform:widget>` for more information.
    """

    #: The name of the column from where we extract UUID value. Defauts to ``uuid``.
    match_column = "uuid"

    def __init__(self, model, match_column=None):
        super().__init__(model)
        if match_column:
            self.match_column = match_column

    def preprocess_cstruct_value(self, node, cstruct):
        """Parse incoming form values to Python objects if needed.
        """
        return slug_to_uuid(cstruct)

    def preprocess_appstruct_value(self, node: colander.SchemaNode, appstruct: set) -> t.List[str]:
        """Convert items to appstruct ids.
        """
        return uuid_to_slug(getattr(appstruct, self.match_column))


class UUIDModelSet(ModelSet):
    """A set of SQLAlchemy objects queried by base64 encoded UUID value.

    See :ref:`Widgets <deform:widget>` for more information.
    """

    match_column = "uuid"

    def __init__(self, model: type=None, match_column: str=None):
        if model:
            self.model = model

        if match_column:
            self.match_column = match_column

    def preprocess_cstruct_values(self, node, cstruct):
        """Parse incoming form values to Python objects if needed.
        """
        return [slug_to_uuid(v) for v in cstruct]

    def preprocess_appstruct_values(self, node: colander.SchemaNode, appstruct: set) -> t.List[str]:
        """Convert items to appstruct ids.
        """
        return [uuid_to_slug(getattr(i, self.match_column)) for i in appstruct]
