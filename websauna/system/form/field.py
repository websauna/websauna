"""Map SQLAlchemy columns and other class attributes to Colander schema.

Also encapsulate :term:`colanderalchemy` so that we don't need to directly expose it in the case we want to get rid of it later.
"""
import colander
import deform
from abc import ABC, abstractmethod
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB, INET
from sqlalchemy.sql.type_api import TypeEngine
from websauna.system.crud import Resource
from websauna.system.form.colander import PropertyAwareSQLAlchemySchemaNode
from websauna.system.form.widget import FriendlyUUIDWidget
from websauna.system.http import Request

from websauna.compat.typing import List
from websauna.compat.typing import Tuple


class ColumnToFieldMapper(ABC):
    """A helper class to map a SQLAlchemy model to Colander/Deform form."""

    @abstractmethod
    def map(self, request:Request, context:Resource, model:type, includes:List) -> colander.SchemaNode:
        """Map a model to a Colander form schema.

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

    def map_column(self, node:colander.SchemaNode, name:str, column:Column, column_type:TypeEngine) -> Tuple[colander.SchemaType, dict]:
        if isinstance(column_type, PostgreSQLUUID):
            return UUID(), dict(missing=colander.drop, widget=FriendlyUUIDWidget(readonly=True))
        elif isinstance(column_type, JSONB):
            return colander.String(), {}
        elif isinstance(column_type, INET):
            return colander.String(), {}
        else:
            # Default mapping / unknown
            return None, {}

    def map(self, request:Request, context:Resource, model:type, includes:List) -> colander.SchemaNode:
        schema = PropertyAwareSQLAlchemySchemaNode(model, includes=includes, type_overrides=self.map_column)
        return schema


class UUID(colander.String):
    """UUID mapping for Colander."""

    def serialize(self, node, appstruct):
        # Assume widgets can handle raw UUID object
        return appstruct
