"""Deform CSRF token support."""
import colander
import deform
from pyramid_deform import deferred_csrf_validator
from pyramid_deform import deferred_csrf_value


def add_csrf(schema: colander.Schema):
    """Add a hidden CSRF field on the schema."""
    csrf_token = colander.SchemaNode(colander.String(), name="csrf_token", widget=deform.widget.HiddenWidget(), default=deferred_csrf_value, validator=deferred_csrf_validator,)

    schema.add(csrf_token)
