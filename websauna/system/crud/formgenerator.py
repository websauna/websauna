"""Abstraction over generating Deform forms from different CRUD models.

This is used by CRUD/admin to create a form for a model to edit. Model doesn't need to be any particular kind. SQLAlchemy is supported by default.
"""
import colander
import deform
from abc import abstractmethod

from websauna.compat.typing import Callable
from websauna.compat.typing import List

from websauna.system.form.fieldmapper import DefaultSQLAlchemyFieldMapper
from websauna.system.form.resourceregistry import ResourceRegistry
from websauna.system.form.editmode import EditMode
from websauna.system.http import Request
from websauna.system.form.schema import add_csrf


def default_schema_binder(schema: colander.Schema, request: Request, context: object, **kwargs):
    """Initialize Colander field dynamic default values. By default, don't do anything.
    By default pass ``request`` and ``context`` to schema.
    """
    return schema.bind(request=request, context=context)


def _noop_customizer(**kwargs):
    return


class FormGenerator:
    """Generate a Deform form.

    :param schema_customizer: is callback ``customize_schema(schema=schema, request=request, context=context, mode=mode, model=model)`` and can dynamically adjust generated form schema after its generation. Customizers edits schema in place and does not return anything.

    :param schema_binder: is callback ``bind_schema(schema=schema, request=request, context=context, mode=mode, model=model)``. It should call ``schema.bind()`` and pass any extra arguments for Colander schema binding.

    By default we usually pass:

    .. code-block:: python

        schema.bind(request=request, context=context)

    """

    def __init__(self, schema_customizer: Callable=None, schema_binder: Callable=None):
        self.schema_customizer = schema_customizer
        self.schema_binder = schema_binder

    @abstractmethod
    def generate_form(self, request: Request, context: object, mode: EditMode, buttons: List[deform.Button], model: type) -> deform.Form:
        """
        :param request: Current HTTP request
        :param context: Traversal context
        :param mode: Of of different form edit modes
        :param buttons: List of form buttons
        :param model: SQLAlchemy model class
        :return: Constructed form object
        """

    def create_deform(self, schema: colander.Schema, request: Request, context: object, mode: EditMode, buttons: List[deform.Button], model: type) -> deform.Form:
        """Create a Deform based on a given generated schema.

        This

        * Adds CSRF token to schema

        * Calles schema customizer

        * Binds schema to request and context or calls custom schema binder

        * Creates the form instance
        """

        # Make sure we have CSRF token

        add_csrf(schema)

        # Customize schema
        customizer = self.schema_customizer or _noop_customizer
        customizer(schema=schema, request=request, context=context, mode=mode, model=model)

        # Bind schema
        binder = default_schema_binder or self.schema_binder
        schema = binder(schema=schema, request=request, context=context, mode=mode, model=model)

        form = deform.Form(schema, buttons=buttons, resource_registry=ResourceRegistry(request))
        return form


class SQLAlchemyFormGenerator(FormGenerator):
    """Automatically create a Deform form from underlying SQLALchemy model.

    :param includes: This is a list of [column name, colander.SchemaNode] we extract from the SQLAlchemy model and generate fields for. If you supply a column name as a string the schema type and widget is automatically resolved. If you give ``colander.SchemaNode(name=name)`` then this schema type is explicitly used, regardless if such a column exist in the model or not.

    If ``includes`` is set to ``None`` it tries to convert all columns to fields it sees on a model.

    For example use case see :py:class:`websauna.system.user.adminviews.UserAdd`.
    """
    
    def __init__(self, includes=None, field_mapper=DefaultSQLAlchemyFieldMapper(), customize_schema: Callable=None, schema_binder: Callable=None):
        self.includes = includes
        self.field_mapper = field_mapper
        super(SQLAlchemyFormGenerator, self).__init__(customize_schema, schema_binder)

    def generate_form(self, request: Request, context: object, mode: EditMode, buttons: List[deform.Button], model: type) -> deform.Form:
        schema = self.field_mapper.map(mode, request, context, model, self.includes, nested=True)
        return self.create_deform(schema, request, context, mode, buttons, model)