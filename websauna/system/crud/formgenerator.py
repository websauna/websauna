"""Abstraction over generating Deform forms from different CRUD models.

This is used by CRUD/admin to create a form for a model to edit. Model doesn't need to be any particular kind. SQLAlchemy is supported by default.
"""
# Standard Library
import typing as t
from abc import abstractmethod

# Pyramid
import colander
import deform

# Websauna
from websauna.system.form.editmode import EditMode
from websauna.system.form.fieldmapper import DefaultSQLAlchemyFieldMapper
from websauna.system.form.resourceregistry import ResourceRegistry
from websauna.system.form.schema import add_csrf
from websauna.system.http import Request

from . import Resource


def default_schema_binder(schema: colander.Schema, request: Request, context: Resource, **kwargs) -> colander.Schema:
    """Initialize Colander field dynamic default values.

    By default, don't do anything and pass ``request`` and ``context`` to schema.

    :param schema: A colander Schema.
    :param request: Current HTTP Request.
    :param context: Traversal context
    :param kwargs: Optional keyword arguments (not used atm)
    :return: Bound colander.Schema
    """
    return schema.bind(request=request, context=context)


def _noop_customizer(**kwargs):
    return


class FormGenerator:
    """Generate a Deform form.

    :param schema_customizer: is a callback ``customize_schema(schema=schema, request=request, context=context, mode=mode, model=model)`` and can dynamically adjust generated form schema after its generation. Customizers edits schema in place and does not return anything.

    :param schema_binder: is a callback ``bind_schema(schema=schema, request=request, context=context, mode=mode, model=model)``. It should call ``schema.bind()`` and pass any extra arguments for Colander schema binding.

    By default we usually pass:

    .. code-block:: python

        schema.bind(request=request, context=context)

    """

    def __init__(self, schema_customizer: t.Callable=None, schema_binder: t.Callable=None):
        """Initialize Form Generator."""
        self.schema_customizer = schema_customizer
        self.schema_binder = schema_binder

    @abstractmethod
    def generate_form(self, request: Request, context: Resource, mode: EditMode, buttons: t.List[deform.Button], model: type) -> deform.Form:
        """Generate form.

        :param request: Current HTTP request
        :param context: Traversal context
        :param mode: Of of different form edit modes
        :param buttons: List of form buttons
        :param model: SQLAlchemy model class
        :return: Constructed form object
        """

    def create_deform(self, schema: colander.Schema, request: Request, context: Resource, mode: EditMode, buttons: t.List[deform.Button], model: type) -> deform.Form:
        """Create a Deform based on a given generated schema.

        This method does the following:

            * Adds CSRF token to schema

            * Calls schema customizer

            * Binds schema to request and context or calls custom schema binder

            * Creates the form instance

        :param schema: Schema to be used.
        :param request: Current HTTP request.
        :param context: Traversal context.
        :param mode: Form mode.
        :param buttons: List of buttons to be added.
        :param model: SQLAlchemy model class
        :return: Constructed form object
        """
        # Make sure we have CSRF token
        add_csrf(schema)

        # Customize schema
        customizer = self.schema_customizer or _noop_customizer
        customizer(schema=schema, request=request, context=context, mode=mode, model=model)

        # Bind schema
        binder = self.schema_binder or default_schema_binder
        schema = binder(schema=schema, request=request, context=context, mode=mode, model=model)

        form = deform.Form(schema, buttons=buttons, resource_registry=ResourceRegistry(request))
        return form


class SQLAlchemyFormGenerator(FormGenerator):
    """Automatically create a Deform form from underlying SQLAlchemy model.

    :param includes: This is a list of [column name, colander.SchemaNode] we extract from the SQLAlchemy model and generate fields for. If you supply a column name as a string the schema type and widget is automatically resolved. If you give ``colander.SchemaNode(name=name)`` then this schema type is explicitly used, regardless if such a column exist in the model or not.

    If ``includes`` is set to ``None`` it tries to convert all columns to fields it sees on a model.

    For example use case see :py:class:`websauna.system.user.adminviews.UserAdd`.
    """

    def __init__(self, includes=None, field_mapper=DefaultSQLAlchemyFieldMapper(), customize_schema: t.Callable=None, schema_binder: t.Callable=None):
        """Initialize SQLAlchemyFormGenerator."""
        self.includes = includes
        self.field_mapper = field_mapper
        super(SQLAlchemyFormGenerator, self).__init__(customize_schema, schema_binder)

    def generate_form(self, request: Request, context: Resource, mode: EditMode, buttons: t.List[deform.Button], model: type) -> deform.Form:
        """Generate form.

        :param request: Current HTTP request
        :param context: Traversal context
        :param mode: Of of different form edit modes
        :param buttons: List of form buttons
        :param model: SQLAlchemy model class
        :return: Constructed form object
        """
        schema = self.field_mapper.map(mode, request, context, model, self.includes, nested=True)
        return self.create_deform(schema, request, context, mode, buttons, model)
