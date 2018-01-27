"""Extra widgets.

Mostly for high level integration.
"""
# Standard Library
import json

# Pyramid
import deform
from colander import null

# Websauna
from websauna.utils.slug import uuid_to_slug


class FriendlyUUIDWidget(deform.widget.TextInputWidget):
    """Display both UUID and base64 encoded string of a stored UUID value.

    For :py:class:`websauna.form.field.UUID` Colander type.
    """

    readonly_template = 'readonly/uuid'

    def get_template_values(self, field, cstruct, kw):
        values = {'cstruct': str(cstruct), 'field': field, 'slug': uuid_to_slug(cstruct) if cstruct else ''}
        values.update(kw)
        values.pop('template', None)
        return values


JSON_PREFORMATTED_STYLE = "font-family: monospace"


class JSONWidget(deform.widget.TextAreaWidget):
    """Nice JSON editor.

    Prettyprints outgoing JSON for better readability.

    Example usage:

    .. code-block:: python

        import colander

        from websauna.system.form.fields import JSONValue
        from websauna.system.form.widgets import JSONWidget

        class MySchema(colander.Schema):

            other_data = colander.SchemaNode(
                JSONValue(),
                widget=JSONWidget(),
                description="JSON bag of attributes of the object",
                missing=dict)

    """

    readonly_template = 'readonly/json'

    def __init__(self, cols=80, rows=10, style=JSON_PREFORMATTED_STYLE, prettyprint=True, **kwargs):
        super(JSONWidget, self).__init__(cols=cols, rows=rows, style=style, **kwargs)
        self.prettyprint = prettyprint

    def process_prettyprint(self, cstruct: str):
        if self.prettyprint:
            try:
                cstruct = json.loads(cstruct)
                return json.dumps(cstruct, sort_keys=True, indent=4)
            except Exception as e:
                pass

        return cstruct

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)

        values["cstruct"] = self.process_prettyprint(values["cstruct"])
        return field.renderer(template, **values)
