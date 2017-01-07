.. _columns:

=======
Columns
=======

.. contents:: :local:

Introduction
============

This chapter discusses of different available :term:`SQL` column types you can use for data modelling.

Basic column types
==================

For available model column types see

* `Column and Data types <http://docs.sqlalchemy.org/en/latest/core/types.html>`_ in SQLAlchemy documentation

* `PostgreSQL ARRAY <http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#array-types>`_

* `PostgreSQL JSON  <http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#json-types>`_

* `PostgreSQL ENUM <http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#enum-types>`_

* :py:class:`sqlalchemy.dialects.postgresql.INET`

* :py:class:`sqlalchemy.dialects.postgresql.UUID`

* :py:class:`sqlalchemy.dialects.postgresql.JSONB`

.. _datetime:

Dates and times
===============

UTC-awareness
-------------

Even though modern SQL databases support timezone aware datetimes, it is recommended that you convert and store all time fields in :term:`UTC` in SQL database. More on background on this in :ref:`Datetime chapter <datetime>`.

To prevent timezone related errors, Websauna has a special column type :py:class:`websauna.system.model.sqlalchemyutcdatetime.UTCDateTime` which contains validation that your datetimes objects are explicitly set to UTC timezone before writing into a database.

.. code-block:: python

    from sqlalchemy import Column

    websauna.system.model.sqlalchemyutcdatetime import UTCDateTime

    class MyModel(Base):
        my_event_at = Column(UTCDateTime)


    dt = random_time_time()  # Assume we pull a Python datetime instance from somewhere

    m = MyModel()
    m.my_event_at = dt

Is almost equal to:

.. code-block:: python

    import datetime

    from sqlalchemy import Column
    from sqlalchemy import DateTime

    class MyModel(Base):
        my_event_at = Column(DateTime)

    dt = random_time_time()  # Assume we pull a Python datetime instance from somewhere

    m = MyModel()
    # This will raise an exception is Python datetime
    # object does not know for which timezone it belongs
    m.my_event_at = dt.astimezone(datetime.timezone.utc)

Enforcing uniqueness
====================

Uniqueness ensures the database cannot have two rows with the same column values. Declaring unique is very useful for "get or create" like functionality.

Single column uniqueness
------------------------

Use ``unique`` attribute in the column declaration. Example:

.. code-block:: python

    class Box(Base):

        __tablename__ = "boxy"

        id = Column(UUID(as_uuid=True), primary_key=True, server_default=sqlalchemy.text("uuid_generate_v4()"))

        #: Box's serial number as in the device
        serial_number = Column(LargeBinary(length=16), unique=True, nullable=True)

Uniqueness across multiple columns
==================================

.. code-block:: python

    from sqlalchemy import UniqueConstraint


    class BoxEvent(Base):

        __tablename__ = "box_event"

        #: Id must be externally set, it is not generated
        id = Column(UUID(as_uuid=True), primary_key=True, server_default=sqlalchemy.text("uuid_generate_v4()"))

        #: When this event originally happened
        happened_at = Column(UTCDateTime, nullable=False)

        #: Make sure for each box there can be only one event happened at a certain time
        __table_args__ = (UniqueConstraint('box_id', 'happened_at', name='box_event_only_once'), )


More information

* http://docs.sqlalchemy.org/en/latest/core/constraints.html

* http://stackoverflow.com/questions/10059345/sqlalchemy-unique-across-multiple-columns

* http://stackoverflow.com/questions/26092756/sqlalchemy-enforcing-a-two-column-unique-constraint-where-one-column-needs-to

Enums
=====

:term:`SQLAlchemy` 1.1 support native Python enums for :term:`PostgreSQL`.

TODO: Show enum patterns

Listing enums
-------------

:term:`PostgreSQL` client like :ref:`ws-db-shell` can list enums with the command::

    \dT+

Migrations
----------

:term:`Alembic` 1.1 cannot automatically migrate enum column types. If you are adding new enum values try following.

* Generate a migration script using ``ws-alembic`` command

* Use ``ALTER TYPE`` directly in your hand edited Alembic migration script

Example:

.. code-block:: python

    def upgrade():

        # Drop transaction isolation level
        connection = None
        if not op.get_context().as_sql:
            connection = op.get_bind()
            connection.execution_options(isolation_level='AUTOCOMMIT')

        # Update enum values
        conn = op.get_bind()
        conn.execute("ALTER TYPE assetcontenttype ADD value 'facebook_post' after 'rss';")
        conn.execute("ALTER TYPE assetcontenttype ADD value 'article' after 'rss';")
        conn.execute("ALTER TYPE assetcontenttype ADD value 'research' after 'rss';")

        # Set transaction isolation level back
        if connection is not None:
            connection.execution_options(isolation_level='READ_COMMITTED')

More info

* https://bitbucket.org/zzzeek/alembic/issues/123/a-way-to-run-non-transactional-ddl

Renaming enums
--------------

:term:`Alembic` migration scripts cannot detect enum item changes. You can manually rename enums using the syntax

.. code-block:: sql

    UPDATE pg_enum SET enumlabel = 'new_enum_label'  WHERE enumlabel = 'old_enum_label' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'my_enum_name')

`More information <http://stackoverflow.com/a/12628411/315168>`_.
