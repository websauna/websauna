# Standard Library
import typing as t

# Pyramid
from pyramid.interfaces import ILocation
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
    """Marker interface telling that Resource class is iterable.

    Database loading example implementation:

    .. code-block:: python

        @implementer(IContainer)
        class AssetFolder(Resource):

            def __getitem__(self, slug: str) -> AssetDescription:

                for asset in self.request.dbsession.query(Asset).filter(Asset.network_id==self.get_network().id):
                    if asset.slug == slug:
                        return self.get_description(asset)

                raise KeyError()

            def items(self):
                for asset_resource in self.get_public_assets():
                    yield asset_resource.__name__, asset_resource

            def get_public_assets(self) -> Iterable[AssetDescription]:
                network = self.get_network()
                dbsession = self.request.dbsession
                for asset in dbsession.query(Asset).filter_by(network=network, state=AssetState.public).order_by(Asset.name.asc()):
                    yield self.get_description(asset)

    Static child example implementation:

    .. code-block:: python

        @implementer(IContainer)
        class NetworkDescription(Resource):

            def items(self):
                yield "assets", self.asset_folder

            def __getitem__(self, item):
                if item == "assets":
                    return self.asset_folder
                raise KeyError()

    For more example implementation see :py:mod:`websauna.tests.sitemapsamples`.

    TODO: Not sure if items() is the best way to do the child discovery. All ideas accepted.
    """

    def items() -> t.Iterable[t.Tuple[str, ILocation]]:
        """Return children in this container as (id, Resource instance) tuples.

        This usually dynamically populates from the database when this is called and there is no caching. The result is iterable only once.

        :return: Iterable (URL id, child object). Child objects can be any Python objects with `__parent__` pointer set as described by a generic interface :py:class:`pyramid.interfaces.ILocation`.
        """
