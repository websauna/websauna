=========================
Modelling with SQLAlchemy
=========================

.. contents:: :local:

Introduction
============

Websauna data modeling are based on :term:`SQLALchemy` library. SQLAlchemy provides a full suite of well known enterprise-level persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language.

Getting started
===============

See :ref:`Getting started <gettingstarted>` tutorial for more handheld introduction.

Creating models
===============

The basic pattern of a model creation is the following:

.. code-block::

    import sys
    import datetime
    from uuid import uuid4

    from sqlalchemy import Column, String, Integer, ForeignKey
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship
    from websauna.system import Initializer

    from websauna.system.model.meta import Base
    from websauna.system.model.columns import UTCDateTime

    from websauna.utils.time import now


    class Question(Base):

        #: The table in the database
        __tablename__ = "question"

        #: Database primary key for the row (running counter)
        id = Column(Integer, autoincrement=True, primary_key=True)

        #: Publicly exposed non-guessable
        uuid = Column(UUID(as_uuid=True), default=uuid4)

        #: Question text
        question_text = Column(String(256), default=None)

        #: When this question was published
        published_at = Column(UTCDateTime, default=None)

Below is a destructing of the example code.

Base class
----------

Websauna provides a model base class :py:class:`websauna.system.model.meta.Base`. If you inherit from this base class all your models become automatically part of migration and initialization cycle. However you are free to choose not to do so, for example if you are integrating with a legacy base. There are several complex use cases where different base classes are needed.

If you are planning to build a reusable addon you may choose to declare your model as:

.. code-block::

    class Question:

        #: The table in the database
        __tablename__ = "question"

... and then let later the addon consumer to plug-in the model of base class of their choice in :py:class:`websauna.system.Initializer.configure_instrumented_models` by using :py:class:`websauna.system.model.utils.attach_model_to_base`.

Columns
-------

Each of your

Date and time
-------------

It is recommended that you store dates and datetimes only in :term:`UTC`. For more information see :ref:`Date and time <datetime>` chapter.

Running counter primary key, UUID or both?
------------------------------------------

TODO

Created and updated at timestamps
---------------------------------

.. note ::

    You can also generate these timestamps on database-side, see ``server_default`` in SQLAlchemy documentation.


Accessing item
==============

By UUID
-------

By id
-----

Iterating query
---------------

.. _cascade:

Cascades
========

Deletes can be defined as *cascading* in :term:`SQLAlchemy` model: All items related to the deleted item by :py:class:`sqlalchemy.ForeignKey` are removed. This is usually the wanted behavior if the foreign key cannot be set null (orphaned rows).

Example setup where cascading delete is set effective.

.. code-block:: python

   class Question(Base):

        #: The table in the database
        __tablename__ = "question"

        #: Database primary key for the row (running counter)
        id = Column(Integer, autoincrement=True, primary_key=True)

        #: Relationship mapping between question and choice.
        #: Each choice can have only question.
        #: Deleteing question deletes its choices.
        choices = relationship("Choice",
                               back_populates="question",
                               lazy="dynamic",
                               cascade="all, delete-orphan",
                               single_parent=True)


    class Choice(Base):

        #: The table in the database
        __tablename__ = "choice"

        #: Database primary key for the row (running counter)
        id = Column(Integer, autoincrement=True, primary_key=True)

        #: Which question this choice is part of
        question_id = Column(Integer, ForeignKey('question.id'))
        question = relationship("Question", back_populates="choices")


`Read more about cascading in SQLAlchemy <http://docs.sqlalchemy.org/en/latest/orm/cascades.html>`_.

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
