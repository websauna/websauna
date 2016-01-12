"""Map SQLAlchemy columns and other class attributes to Colander schema.

Also encapsulate :term:`colanderalchemy` so that we don't need to directly expose it in the case we want to get rid of it later.
"""
from enum import Enum
import logging

import colander

from abc import ABC, abstractmethod
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB, INET
from sqlalchemy.sql.type_api import TypeEngine
from websauna.system.crud import Resource
from websauna.system.form.colander import PropertyAwareSQLAlchemySchemaNode, TypeOverridesHandling
from websauna.system.form.widget import FriendlyUUIDWidget
from websauna.system.http import Request

from websauna.compat.typing import List
from websauna.compat.typing import Tuple

from . import fields


logger = logging.getLogger(__name__)


class EditMode(Enum):
    """Different edit modes for form creation."""
    show = 0
    add = 1
    edit = 2


class ColumnToFieldMapper(ABC):
    """A helper class to map a SQLAlchemy model to Colander/Deform form."""

    @abstractmethod
    def map(self, mode:EditMode, request:Request, context:Resource, model:type, includes:List) -> colander.SchemaNode:
        """Map a model to a Colander form schema.

        :param mode: IS this add, edit or show form. For example, some relationship fields do not make sense on add form.

        :param context: Resource with ``get_object()`` to get the actual SQLAlchemy object

        :param model: SQLAlchemy model class

        :param includes: List of [column name | SchemaNode] we need to map

        :return: colander.SchemaNode which presents the automatically generated form
        """


class DefaultFieldMapper(ColumnToFieldMapper):
    """The default SQLAlchemy to form field and widget mapping implementation.

    We support

    * the default colanderalchemy mappings

    * UUID

    * JSONProperty declarations

    See :py:class:`colanderalchemy.schema.SQLAlchemySchemaNode` for more information.
    """

    def map_column(self, mode:EditMode, node:colander.SchemaNode, name:str, column:Column, column_type:TypeEngine) -> Tuple[colander.SchemaType, dict]:

        logger.debug("Mapping field %s, mode %s, node %s, column %s", name, mode, node, column)

        # Never add primary keys
        # NOTE: TODO: We need to preserve ids because of nesting mechanism and groupedit widget wants it id
        if column.primary_key:
            # TODO: Looks like column.autoincrement is set True by default, so we cannot use it here
            if mode in (EditMode.edit, EditMode.add):
                return TypeOverridesHandling.drop, {}

        if isinstance(column_type, PostgreSQLUUID):

            # UUID's cannot be edited
            if mode in (EditMode.add, EditMode.edit):
                return TypeOverridesHandling.drop, {}

            # But let's show them
            return fields.UUID(), dict(missing=colander.drop, widget=FriendlyUUIDWidget(readonly=True))
        elif isinstance(column_type, JSONB):

            # Can't edit JSON
            if mode in (EditMode.add, EditMode.edit):
                return TypeOverridesHandling.drop, {}

            return colander.String(), {}
        elif isinstance(column_type, INET):
            return colander.String(), {}
        else:
            # Default mapping / unknown, let the parent handle
            return TypeOverridesHandling.unknown, {}

    def map(self, mode:EditMode, request:Request, context:Resource, model:type, includes:List, nested=None) -> colander.SchemaNode:

        def _map_column(node, name, column, column_type):
            return self.map_column(mode, node, name, column, column_type)

        # Don't try to pull in relatinoships on add form
        if nested is None:
            nested = (mode in (EditMode.edit, EditMode.show))

        schema = PropertyAwareSQLAlchemySchemaNode(model, includes=includes, type_overrides=_map_column, nested=nested)
        return schema


