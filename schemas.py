import deform
import deform.widget as w
import colander as c

from horus.schemas import unique_email

from horus.models import _


class RegisterSchema(CSRFSchema):

    email = c.SchemaNode(
        c.String(),
        title=_('Email'),
        validator=c.All(c.Email(), unique_email),
        description=_("Example: joe@example.com"),
        widget=w.TextInputWidget(size=40, maxlength=260, type='email'))

    password = c.SchemaNode(
        c.String(),
        validator=c.Length(min=6),
        widget=deform.widget.CheckedPasswordWidget(),
    )

