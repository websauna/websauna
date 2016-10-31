from pyramid.interfaces import ILocation
from websauna.compat.typing import Iterable
from websauna.compat.typing import Tuple

from zope.interface import Interface


class IRoot(Interface):
    """Market interface for the root object.

    Used e.g. breadcrumbs and traversing are we in root tests.
    """


class ISecrets(Interface):
    """Utility marker interface which gives us our secrets.

    Secrets is a dictionary which hold sensitive deployment data.
    """

class IContainer(ILocation):
    """Marker interface telling that Resource class is iterable."""

    def items() -> Iterable[Tuple[str, ILocation]]:
        """Return children in this container as (id, Resource instance) tuples.

        This usually dynamically populates from the database when this is called and there is no caching. The result is iterable only once.

        All results must have their ``__parent__`` pointer set.
        """