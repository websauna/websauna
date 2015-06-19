"""Extra colanderalchemy model<->form mappings for SQLAlchemy types."""
from sqlalchemy import types
from sqlalchemy.dialects import postgresql

import colander


class INET(types.TypeDecorator):
    """Map PostgreSQL IP addresses to the Stringg editor in form.

    TODO: For now, only readonly support.
    """

    impl = postgresql.INET

    __colanderalchemy_config__ = {'typ':colander.String()}