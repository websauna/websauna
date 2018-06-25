"""Map SQLAlchemy columns and other class attributes to Colander schema.

Also encapsulate :term:`colanderalchemy` so that we don't need to directly expose it in the case we want to get rid of it later.
"""
# Standard Library
import logging
import typing as t
from abc import ABC
from abc import abstractmethod

# Pyramid
import colander
import deform

# SQLAlchemy
from sqlalchemy import Column
from sqlalchemy import LargeBinary
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative.clsregistry import _class_resolver
from sqlalchemy.orm import Mapper
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql.type_api import TypeEngine

# Websauna
from websauna.system.crud import Resource
from websauna.system.form.colander import PropertyAwareSQLAlchemySchemaNode
from websauna.system.form.colander import TypeOverridesHandling
from websauna.system.form.fields import JSONValue
from websauna.system.form.sqlalchemy import UUIDForeignKeyValue
from websauna.system.form.sqlalchemy import UUIDModelSet
from websauna.system.form.sqlalchemy import get_uuid_vocabulary_for_model
from websauna.system.form.widgets import FriendlyUUIDWidget
from websauna.system.form.widgets import JSONWidget
from websauna.system.http import Request
from websauna.system.model import columns

from . import fields
from .editmode import EditMode


# TODO: Clean this up when getting rid of colanderalchemy
try:
    # Temporary support to suppress problematic form generation with geoalchemy
    from geoalchemy2 import Geometry
except ImportError:
    Geometry = ()


logger = logging.getLogger(__name__)


class ColumnToFieldMapper(ABC):
    """A helper class to map a SQLAlchemy model to Colander/Deform form."""

    @abstractmethod
    def map(self, mode: EditMode, request: Request, context: Resource, model: type, includes: t.List) -> colander.SchemaNode:
        """Map a model to a Colander form schema.

        :param mode: IS this add, edit or show form. For example, some relationship fields do not make sense on add form.

        :param context: Resource with ``get_object()`` to get the actual SQLAlchemy object

        :param model: SQLAlchemy model class

        :param includes: List of [column name | SchemaNode] we need to map

        :return: colander.SchemaNode which presents the automatically generated form
        """


class DefaultSQLAlchemyFieldMapper(ColumnToFieldMapper):
    """The default SQLAlchemy to form field and widget mapping implementation.

    We support

    * The default colanderalchemy mappings

    * UUID

    * JSONProperty declarations

    * IP addresses (INET)

    * ForeignKey references where it holds a reference to one another SQLAlchemy object

    See :py:class:`colanderalchemy.schema.SQLAlchemySchemaNode` for more information.
    """

    def map_standard_relationship(self, mode, request, node, model, name, rel) -> colander.SchemaNode:
        """Build a widget for choosing a relationship with target.

        The relationship must be foreign_key and the remote must offer ``uuid`` attribute which we use as a vocabulary key..
        """

        if isinstance(rel.argument, Mapper):
            # TODO: How to handle this kind of relationships
            return TypeOverridesHandling.drop

        if isinstance(rel.argument, _class_resolver):
            # Case from tutorialapp:
            # <RelationshipProperty at 0x1095a4438; question>
            # <class 'sqlalchemy.ext.declarative.clsregistry._class_resolver'>
            remote_model = rel.argument()
        else:
            remote_model = rel.argument

        # Get first column of the set
        for column in rel.local_columns:
            break

        # For now, we automatically deal with this only if the model provides uuid
        if hasattr(remote_model, "uuid"):
            dbsession = request.dbsession
            # TODO: We probably need a mechanism for system wide empty default label

            required = not column.nullable

            if mode in (EditMode.add, EditMode.edit):
                default_choice = "--- Choose one ---"
            else:
                default_choice = "(not set)"

            if required:
                missing = colander.required
            else:
                missing = None

            vocabulary = get_uuid_vocabulary_for_model(dbsession, remote_model, default_choice=default_choice)

            if rel.uselist:
                # Show out all relationships
                if mode == EditMode.show:
                    return colander.SchemaNode(UUIDModelSet(remote_model), name=name, missing=missing, widget=deform.widget.CheckboxChoiceWidget(values=vocabulary))
            else:
                # Select from a single relationship
                return colander.SchemaNode(UUIDForeignKeyValue(remote_model), name=name, missing=missing, widget=deform.widget.SelectWidget(values=vocabulary))

        return TypeOverridesHandling.drop

    def map_relationship(self, mode: EditMode, request: Request, node: colander.SchemaNode, model: type, name: str, rel: RelationshipProperty, mapper: Mapper):

        # Ok this is something we can handle, a single reference to another
        return self.map_standard_relationship(mode, request, node, model, name, rel)

    def map_column(self, mode: EditMode, request: Request, node: colander.SchemaNode, model: type, name: str, column: Column, column_type: TypeEngine) -> t.Tuple[colander.SchemaType, dict]:
        """Map non-relationship SQLAlchemy column to Colander SchemaNode.

        :return: Tuple(constructed colander.SchemaType, dict of addtional colander.SchemaNode construction arguments)
        """
        logger.debug("Mapping field %s, mode %s, node %s, column %s, column type %s", name, mode, node, column, column_type)

        # Check for autogenerated columns (updated_at)
        if column.onupdate:
            if mode in (EditMode.edit, EditMode.add):
                return TypeOverridesHandling.drop, {}

        # Don't fill default values when added, as they are automatically populated
        if column.default:
            if mode == EditMode.add:
                return TypeOverridesHandling.drop, {}

        # Never add primary keys
        # NOTE: TODO: We need to preserve ids because of nesting mechanism and groupedit widget wants it id
        if column.primary_key:
            # TODO: Looks like column.autoincrement is set True by default, so we cannot use it here
            # if mode in (EditMode.edit, EditMode.add):
                # return TypeOverridesHandling.drop, {}
            return TypeOverridesHandling.drop, {}

        if column.foreign_keys:

            # Handled by relationship mapper
            return TypeOverridesHandling.drop, {}

        elif isinstance(column_type, (PostgreSQLUUID, columns.UUID)):

            # UUID's cannot be22 edited
            if mode in (EditMode.add, EditMode.edit):
                return TypeOverridesHandling.drop, {}

            # But let's show them
            return fields.UUID(), dict(missing=colander.drop, widget=FriendlyUUIDWidget(readonly=True))

        elif isinstance(column_type, Text):
            return colander.String(), dict(widget=deform.widget.TextAreaWidget())
        elif isinstance(column_type, JSONB):
            return JSONValue(), dict(widget=JSONWidget())
        elif isinstance(column_type, LargeBinary):
            # Can't edit binary
            return TypeOverridesHandling.drop, {}
        elif isinstance(column_type, Geometry):
            # Can't edit geometry
            return TypeOverridesHandling.drop, {}
        elif isinstance(column_type, (INET, columns.INET)):
            return colander.String(), {}
        else:
            # Default mapping / unknown, let the parent handle
            return TypeOverridesHandling.unknown, {}

    def map(self, mode: EditMode, request: Request, context: t.Optional[Resource], model: type, includes: t.List, nested=None) -> colander.SchemaNode:
        """
        :param mode: What kind of form is this - show, add, edit
        :param request: HTTP request
        :param context: Current traversing context or None
        :param model: The SQLAlchemy model class for which we generate schema
        :param includes: List of column, relationship and property names or ``colander.SchemaNode(name=name)`` instances to be included on the form.
        :param nested: Legacy. Going away.
        """

        def _map_column(node, name, column, column_type):
            # if name == 'email':
                # import pdb; pdb.set_trace()
            return self.map_column(mode, request, node, model, name, column, column_type)

        def _map_relationship(node: colander.SchemaNode, name: str, prop: RelationshipProperty, mapper: Mapper):
            return self.map_relationship(mode, request, node, model, name, prop, mapper)

        # TODO: We need to get rid of nested
        # Don't try to pull in relatinoships on add form
        nested = True

        # TODO: Make explicitly passed
        dbsession = request.dbsession

        schema = PropertyAwareSQLAlchemySchemaNode(model, dbsession, includes=includes, type_overrides=_map_column, relationship_overrides=_map_relationship, automatic_relationships=True, nested=nested)
        return schema
