"""Extra widgets.

Mostly for high level integration.
"""

import deform
from deform.widget import _normalize_choices
from websauna.utils.slug import uuid_to_slug


class FriendlyUUIDWidget(deform.widget.TextInputWidget):
    """Display both UUID and base64 encoded string of a stored UUID value.

    For :py:class:`websauna.form.field.UUID` Colander type.
    """

    readonly_template = 'readonly/uuid'

    def get_template_values(self, field, cstruct, kw):
        values = {'cstruct':str(cstruct), 'field':field, 'slug':uuid_to_slug(cstruct) if cstruct else ''}
        values.update(kw)
        values.pop('template', None)
        return values


JSON_PREFORMATTED_STYLE = "font-family: monospace"


class JSONWidget(deform.widget.TextAreaWidget):
    """Nice JSON editor.
    
    """

    def __init__(self, cols=80, rows=10, style=JSON_PREFORMATTED_STYLE, **kwargs):
        super(JSONWidget, self).__init__(cols=cols, rows=rows, style=style, **kwargs)
