# Pyramid
import colander
import deform


@colander.deferred
def deferred_csrf_value(node, kw):
    return kw['request'].session.get_csrf_token()


class CSRFSchema(colander.Schema):
    """Schema base class which generates CSRF token.

    Example:

    .. code-block:: python

      from websauna.system.form.schema import CSRFSchema
      import colander

      class MySchema(CSRFSchema):
          my_value = colander.SchemaNode(colander.String())

      And in your application code, *bind* the schema, passing the request as a keyword argument:

      .. code-block:: python

        def aview(request):
            schema = MySchema().bind(request=request)

    The token is automatically then verified by Pyramid CSRF view deriver.

    Original code: https://github.com/Pylons/pyramid_deform/blob/master/pyramid_deform/__init__.py
    """
    csrf_token = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        default=deferred_csrf_value,
    )

    csrf_token.dictify_by_default = False


def add_csrf(schema: colander.Schema):
    """Add a hidden csrf_token field on the existing Colander schema."""
    csrf_token = colander.SchemaNode(colander.String(), name="csrf_token", widget=deform.widget.HiddenWidget(), default=deferred_csrf_value)
    csrf_token.dictify_by_default = False
    schema.add(csrf_token)
