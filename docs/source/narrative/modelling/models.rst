=========================
Modelling with SQLAlchemy
=========================

.. contents:: :local:

Introduction
============

Websauna models are based on SQLALchemy.

See Getting started tutorial for more information for now.

Accessing model instance
========================

By UUID
=======

By id
=====

Advanced
========

Get or create pattern
---------------------

Your application may assume there should be some standard, never changing, rows in a database. You can either create there rows beforehand using command line or dynamically using get or create pattern.

Below is an example of get or create pattern which creates two foreign key nested items and returns the latter one::

    from websauna.wallet.models import AssetNetwork
    from websauna.wallet.models import Asset


    def get_or_create_default_asset(dbsession, asset_network_name="Toy bank", asset_name="US Dollar", asset_symbol="USD"):
        """Creates a new fictious asset we use to track toy balances."""

        network = dbsession.query(AssetNetwork).filter_by(name=asset_network_name).first()
        if not network:
            network = AssetNetwork(name=asset_network_name)
            dbsession.add(network)
            dbsession.flush()  # Gives us network.id

        # Now get/create item under asset network
        asset = network.assets.filter_by(name=asset_name).first()
        if not asset:
            asset = Asset(name=asset_name, symbol=asset_symbol)
            network.assets.append(asset)
            dbsession.flush()  # Gives us asset.id
            return asset, True

        return asset, False


.. note ::

    This was written before any PostgreSQL UPSERT support in SQLAlchemy.