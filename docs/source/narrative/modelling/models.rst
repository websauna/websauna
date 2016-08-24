.. _models:

=========================
Modelling with SQLAlchemy
=========================

.. contents:: :local:

Introduction
============

Websauna data modeling are based on :term:`SQLALchemy` library. SQLAlchemy provides a full suite of well known enterprise-level persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language.

Getting started
===============

See :ref:`Websauna's getting started <gettingstarted>` tutorial for more handheld introduction. Peek also into SQLAlchemy's `Object Relation Tutorial <http://docs.sqlalchemy.org/en/latest/orm/tutorial.html>`_.

Creating models
===============

The basic model creation pattern is same as in SQLAlchemy (`SQLAlchemy declarative model documentation <http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/basic_use.html#defining-attributes>`_):

.. code-block:: python

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

Websauna provides a model base class :py:class:`websauna.system.model.meta.Base`. If you inherit from this base class all your models become part of migration and application initialization cycle. However you are free to choose not to do so, for example if you are integrating with a legacy code base. There are several complex use cases where different base classes may be needed.

If you are planning to build a reusable addon you may choose to declare your model as:

.. code-block:: python

    class Question:  # <-- It's just plain Python class

        #: The table in the database
        __tablename__ = "question"

... and then let later the addon consumer to plug-in the model of base class of their choice in :py:class:`websauna.system.Initializer.configure_instrumented_models` by using :py:class:`websauna.system.model.utils.attach_model_to_base`.

.. uuid-security:

Primary keys: UUID, running counter or both?
--------------------------------------------

Websauna has extensively support for using :term:`UUID`, or more specifically UUID version 4 (random), for primary key ids. UUID v4 gives you a 122 bit non-guessable integer with 6 bit for error checking.

.. note ::

    One should never expose a running counter database keys, like a running counter ``id`` to the world. Leaking ids also leaks business intelligence like number of users or number of orders. Furthermore guessable ids give a malicious party the ability to guess URL endpoints, scrape data and exploit other known weaknesses effectively. If possible it is recommended that you do not have any running counter ids on your models to avoid the issue altogether.


UUID column support in databases
++++++++++++++++++++++++++++++++

PostgreSQL and SQLAlchemy have a a native :py:class:`sqlalchemy.dialects.postgresql.UUID` column. For other databases you might want to try a backend agnostic GUID (`see sqlalchemy_utils.types.uuid.UUIDType <https://sqlalchemy-utils.readthedocs.org/en/latest/data_types.html#sqlalchemy_utils.types.uuid.UUIDType>`_).

For complete UUID support it's better to let the database, not your application, generate primary key UUIDs. This way UUIDs are generated correctly even if other non-Python applications use the same database.

PostgreSQL has a `uuid-ossp <http://www.postgresql.org/docs/devel/static/uuid-ossp.html>`_ extension for generating UUIDs.

To enable this extension you must run the following command in :ref:`ws-db-shell` after creating a database:

.. code-block:: sql

    create EXTENSION if not EXISTS "uuid-ossp";

Or just from the command line:

.. code-block:: console

    echo 'create EXTENSION if not EXISTS "uuid-ossp";' | ws-db-shell conf/development.ini

After this, the following works in a column definition:

.. code-block:: python

    uuid = Column(UUID(as_uuid=True),
                server_default=sqlalchemy.text("uuid_generate_v4()"),)

Read blog post `UUID Primary Keys in PostgreSQL <https://blog.starkandwayne.com/2015/05/23/uuid-primary-keys-in-postgresql/>`_.

UUID primary keys
+++++++++++++++++

Secure-wise, the best practice is to use a random UUID ``id`` as a primary key:

.. code-block:: python

    import sqlalchemy
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy import Column


    class Asset(Base):

        __tablename__ = "asset"

        id = Column(UUID(as_uuid=True),
            primary_key=True,
            server_default=sqlalchemy.text("uuid_generate_v4()"),)

As UUIDs are random, one cannot accidentally leak information about item URLs or counts.

The downside is that UUIDs are not very human readable. Accessing objects in shell sessions or communicating ids verbally is tricky. If you need a human readable ID you can generate another shorter string for this purpose.

Converting UUIDs to Base64 strings and back
+++++++++++++++++++++++++++++++++++++++++++

The default string format of an UUID id is longish and not very URL friendly:

.. code-block:: pycon

    >>> import uuid

    >>> u = uuid.uuid4()

    >>> str(u)
    '234a7847-2a08-41ef-8443-5194fd089ca1'

For using UUIDs in web context, Websauna offers two helper methods to UUID :term:`Base64` string presentation

* :py:func:`websauna.utils.slug.uuid_to_slug`

* :py:func:`websauna.utils.slug.slug_to_uuid`

Example:

.. code-block:: pycon

    >>> from websauna.utils import slug

    >>> string_id = slug.uuid_to_slug(u)

    # Compact base64 encoded form
    >>> str(string_id)
    I0p4RyoIQe-EQ1GU_QicoQ

    # Back to UUID object
    >>> print(slug.slug_to_uuid('I0p4RyoIQe-EQ1GU_QicoQ'))
    234a7847-2a08-41ef-8443-5194fd089ca1

.. _running-counter-id:

Running counter id primary key and UUID column
++++++++++++++++++++++++++++++++++++++++++++++

This approach is a combination of both traditional running counter ids (human readable) and non-guessable UUIDs. This is also the approach :ref:`tutorial <gettingstarted>` takes:

.. code-block:: python

    from sqlalchemy import Column, String, Integer, ForeignKey
    from sqlalchemy.dialects.postgresql import UUID


    class Question(Base):

        #: The table in the database
        __tablename__ = "question"

        #: Database primary key for the row (running counter)
        id = Column(Integer, autoincrement=True, primary_key=True)

        #: Publicly exposed non-guessable
        uuid = Column(UUID(as_uuid=True), default=uuid4)


    class Choice(Base):

        # ...

        #: Which question this choice is part of
        question_id = Column(Integer, ForeignKey('question.id'))
        question = relationship("Question", back_populates="choices", uselist=False)


* ``id`` is used internally in foreign keys and not exposed anywhere else than admin. This allows human operators to easily discuss and cognitively track down database rows having issues. For example, you get nice running counter in user admin based on the order of sign ups.

* ``uuid`` is used in all external links. A malicious party cannot potentially guess the URL of any edit form and thus they cannot launch attacks against predefined URLs.

Running counter as a primary key
++++++++++++++++++++++++++++++++

If you have legacy data it is possible to use only running counter ids when referring to data. This includes running counter ids in links too. This is discouraged as this may expose a lot of busines sensitive information (number of users, number of orders) to third parties.

Example:

.. code-block:: python

    from sqlalchemy import Column, String, Integer, ForeignKey


    class BasicIdModel(Base):

        #: The table in the database
        __tablename__ = "basic_id_model"

        #: Database primary key for the row (running counter)
        id = Column(Integer, autoincrement=True, primary_key=True)

Columns
-------

See :ref:`columns`.

Date and time
-------------

It is recommended that you store dates and datetimes only in :term:`UTC`. For more information see :ref:`Date and time <datetime>` chapter.

Created and updated timestamps
------------------------------

The following is a common pattern to add created and updated at timestamps to your models. They provide much convenience when it comes down to diagnose and track issues:

.. code-block:: python

    from websauna.system.model.columns import UTCDateTime

    class User:

        #: When this account was created
        created_at = Column(UTCDateTime, default=now, nullable=False)

        #: When the account data was updated last time
        updated_at = Column(UTCDateTime, onupdate=now, nullable=True)

.. note ::

    You can also generate these timestamps using database functions, see ``server_default`` in SQLAlchemy documentation.

Accessing single item
=====================

First see :ref:`dbsession` information how to get access to database session in different contexts. ``dbsession`` is the root of all SQL queries.

By primary key
--------------

Use :py:meth:`sqlalchemy.orm.Query.get`. Example model:

.. code-block:: python

    class Asset(Base):

        __tablename__ = "asset"

        id = Column(UUID(as_uuid=True),
            primary_key=True,
            server_default=sqlalchemy.text("uuid_generate_v4()"),)

You can get an object using a base64 UUID:

.. code-block:: python

    # Use get() as a shorthand method to get one object by primary key
    >>> from .model import Asset
    >>> from websauna.utils.slug import slug_to_uuid
    >>> uuid = slug_to_uuid('I0p4RyoIQe-EQ1GU_QicoQ')
    >>> dbsession.query(Asset).get(uuid)
    <Asset>

Or if your primary key is a running counter id object:

.. code-block:: python

    class Question(Base):

        #: The table in the database
        __tablename__ = "question"

        #: Database primary key for the row (running counter)
        id = Column(Integer, autoincrement=True, primary_key=True)

.. code-block:: pycon

    # Use get() as a shorthand method to get one object by primary key
    >>> dbsession.query(Question).get(1)
    #1: What's up?

Non-primary key access
----------------------

You can use :py:meth:`sqlalchemy.orm.Query.filter_by` (keyword arguments) or :py:meth:`sqlalchemy.orm.Query.filter` (column object arguments).

:py:meth:`sqlalchemy.orm.Query.one_or_none` returns exactly one or None items. For multiple items an error is raised:

.. code-block:: pycon

    >>> dbsession.query(Question).filter_by(id=1).one_or_none()
    #1: What's up?

:py:meth:`sqlalchemy.orm.Query.first` returns the first item (of multiple items) or ``None``:

.. code-block:: pycon

    >>> dbsession.query(Question).filter(Question.id==1).first()
    #1: What's up?

:py:meth:`sqlalchemy.orm.Query.one` returns one item and raises an error if there are no items or multiple items:

.. code-block:: pycon

    >>> dbsession.query(Question).filter(Question.id==1).one()
    #1: What's up?

Accessing multiple items
========================

The usual access pattern is that you construct a :py:class:`sqlalchemy.orm.Query` object.

* You may join other tables to the query using :py:meth:`sqlalchemy.orm.Query.join` over relationships

Examples models are in :ref:`tutorial <gettingstarted>`.

All items of a model
--------------------

.. code-block:: pycon

    # Let's use model from tutorial
    >> from myapp.models import Question

    >>> dbsession.query(Question).all()
    [#1: What is love?, #2: Where is love?, #3: Why there is love?]

:py:class:`sqlalchemy.orm.Query` is an iterable object, use it with ``for``:

.. code-block:: pycon

    >>> for q in dbsession.query(Question): print(q.id, q.uuid, q.question_text)
    1 d51a3bda-321a-4dfa-b54e-87a5c7a5f5c1 What is love?
    2 fc75588b-90c4-4df0-bd0f-cbcad62f4e7f Where is love?
    3 1e40fd40-bb13-44da-ad4a-e298eaebe0d2 Why there is love?

Filtering queries
-----------------

You narrow down your query using :py:meth:`sqlalchemy.orm.Query.filter_by` (keyword arguments) or :py:meth:`sqlalchemy.orm.Query.filter` (column object arguments).

Using direct keywords with :py:meth:`sqlalchemy.orm.Query.filter_by`:

.. code-block:: pycon

    >>> dbsession.query(Question).filter_by(id=1).first()
    #1: What's up?

Using column objects with :py:meth:`sqlalchemy.orm.Query.filter` and Python comparison operators:

.. code-block:: pycon

    >>> dbsession.query(Question).filter(Question.id >= 2).all()
    [#2: Where is love?, #3: Why there is love?]

Text matching query with :py:meth:`sqlalchemy.schema.Column.like`:

.. code-block:: pycon

    >>> dbsession.query(Question).filter(Question.question_text.like('What%')).all()
    [#1: What's up?]

Using :py:func:`sqlalchehmy.sql.expression.extract` for complex value matching:

.. code-block:: pycon

    >>> dbsession.query(Question).filter(sqlalchemy.extract('year', Question.published_at) == now().year).all()
    [#1: What's up?]

Relationship queries
--------------------

TODO

.. note ::

    When you are accessing child items over a relationship attribute, the resulting object depends if the relationship is set as ``relationship(lazy='dynamic')`` (gives :py:class:`sqlalchemy.orm.Query`) object or the default ``relationship(lazy='select')`` (gives a list). This is important if you want to further filter down the list.

.. _cascade:

Updating items
==============

.. **When I need to commit?**

    TODO

.. note ::

    **Why there is no save()?**

    :term:`SQLAlchemy` has a :term:`state management` mechanism. It tracks what objects you have modified or added via ``dbsession.add()``. On a succesfull commit, all of these changes are written to a database and you do not need to explicitly list what changes need to be saved.

Deleting items
==============

Deleting one item
-----------------

Example:

.. code-block:: Python

    dbsession.delete(obj)

See :py:meth:`sqlalchemy.orm.session.Session.delete` for more information.

Deleting multiple items
-----------------------

.. code-block:: Python

    # Delete all items


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

Relationships
=============

One-to-one
----------

TODO

One-to-many
-----------

TODO

Many-to-many
------------

A normal `SQLALchemy many-to-many pattern <http://docs.sqlalchemy.org/en/rel_0_8/orm/extensions/declarative.html#configuring-many-to-many-relationships>`_ can be used to declare relationships. However one should wrap the mapping table in an :term:`ORM` class, so that :term:`migration` script will pick it up.

Example:

.. code-block:: python

    import sqlalchemy as sa
    from sqlalchemy import orm
    import sqlalchemy.dialects.postgresql as psql

    from websauna.system.model.meta import Base


    class UserCustomer(Base):
        """Many-to-many relationship between users and customers.

        We use raw ``__table__`` to define the relationship table, as per SQLAlchemy documentation: http://docs.sqlalchemy.org/en/rel_0_8/orm/extensions/declarative.html#configuring-many-to-many-relationships

        However, we need to have an ORM class definition, so that our :term:`migration` scripts will pick this table up and create it properly.
        """

        __table__ = sa.Table('user_customer', Base.metadata,

            sa.Column('user_id',
                      sa.ForeignKey("users.id"),
                      primary_key=True),

            sa.Column('customer_id',
                      sa.ForeignKey("customer.id"),
                      primary_key=True)
        )

    class Customer(Base):
        """A customer record imported from a utility company."""

        __tablename__ = "customer"

        #: Our id
        id = sa.Column(psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()"))

        #: Map customers to users and vice versa. One user phone number can address multiple customer records (across different organizations). One customer can have multiple users (corporate shared access).
        users = orm.relationship(User,
                                 secondary=UserCustomer.__table__,
                                 backref=orm.backref("customers", lazy="dynamic"),
                                 lazy="dynamic",
                                 )

Then you can use it as:

.. code-block:: python

    u = User()
    u2 = User()
    dbsession.add(u)
    dbsession.flush()

    c = Customer()
    c.users.append(u)
    c.users.append(u2)
    dbsession.add(c)
    dbsession.flush()

    print(list(c.users))


Advanced
========

Getting a list from a query
---------------------------

*

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

