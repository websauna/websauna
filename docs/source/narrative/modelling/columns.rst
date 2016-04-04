.. _columns:

=======
Columns
=======

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