===================
JSON data in models
===================

Introduction
============

:term:`PostgreSQL` database offers very powerful :term:`JSONB` column which allows store schemaless data easily based on :term:`JSON`. This gives many advantages of "NoSQL"-like databases by still maintaining :term:`ACID` guarantees.

Websauna takes advantage of this and offers integration glue over what :term:`SQLAlchemy` offers by default.

Using JSONB column
==================

Here is a quick example:

.. code-block:: python

    import sqlalchemy as sa
    import sqlalchemy.orm as orm
    import sqlalchemy.dialects.postgresql as psql
    from sqlalchemy.orm import Session
    from websauna.system.model.columns import UTCDateTime

    from websauna.system.model.meta import Base
    from websauna.system.user.models import User
    from websauna.utils.time import now
    from websauna.system.model.json import NestedMutationDict


    class Verification(Base):

        __tablename__ = "verification"

        #: When this was created
        created_at = sa.Column(UTCDateTime, default=now, nullable=False)

        #: When this data was updated last time
        updated_at = sa.Column(UTCDateTime, onupdate=now)

        #: Misc. bag of data like address, phone number we ask from the user
        verification_data = sa.Column(NestedMutationDict.as_mutable(JSONB), default=dict)


Then you can use it like:

.. code-block:: python

    v = Verification()
    v.verification_data["name"] = "Mikko Ohtamaa"
    v.verification_data["hometown"] = "Toholampi"
    dbsession.add(v)
    transaction.commit()

    v = dbsession.query(Verification).first()
    for key, value in v.verification_data.items():
        print("{} is {}".format(key, value))

You can also dictionary data from a random source:

.. code-block:: python

    source_data = {"car": "DeLorean", "color": "red"}
    v = Verification()
    v.verification_data.update(source_data)


More more information see :py:class:`sqlalchemy.dialects.postgresql.JSONB`.

Mutation tracking
-----------------

:py:class:`websauna.system.model.json.NestedMutationDict` provides nested state tracking for JSON column dictionaries.

This means that the following works:

.. code-block:: python

    v = Verification()
    v.verification_data["name"] = "Mikko Ohtamaa"
    dbsession.add(v)
    transaction.commit()

    v = dbsession.query(Verification).first()
    # Plain SQLAlchemy JSONB would not mark v object
    # dirty when we set a dictionary key here.
    # The change would not be stored in the following commit
    v.verification_data["phone_number"] = "+1 505 123 1234"
    transaction.commit()


For more information see :py:mod:`websauna.system.model.json`.

Default usage
-------------

:py:class:`websauna.system.user.usermixin.UserMixin` provides example in the format of ``user_data`` where random user variables and all social media connected data is stored.

Using JSONBProperty
===================

.. note ::

    JSONBProperty is a class planned to be moved out from Websauna project. Please do not use it in your projects as is.

Use cases

* No migration needed when adding new properties

* You can refer inside non-structured data you have dumped on JSON column from external source

* Mutation tracking

Non-JSON serializable types
===========================

By default the following Python data does not serialize as JSON:

* Python's ``Decimal``

* ``datetime``

* UUID

You need to use string presentations for these. For inspiration see the code below:

.. code-block:: python

    """Serialize Python dates and decimals in JSON."""

    import datetime
    import json

    from decimal import Decimal
    from uuid import UUID
    from websauna.utils import dictutil


    class _DecimalEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, Decimal):
                return str(o.quantize(Decimal("1.00")))

            if isinstance(o, datetime.datetime):
                return str(o.isoformat())

            return super(_DecimalEncoder, self).default(o)


    def _fix_data(o):
        if isinstance(o, Decimal):
            return str(o.quantize(Decimal("1.00")))

        if isinstance(o, datetime.datetime):
            return str(o.isoformat())

        if isinstance(o, UUID):
            return str(o)

        return o

    def fix_json_data(obj: Any[list, dict]) -> object:
        """Fixed Python dictionary data in-place to be JSON serializable.

        Converts decimals and datetimes to string presentation.

        :param obj: List or Dictionary
        """
        return dictutil.traverse(obj, _fix_data)


More information
================

`Automatic mutation tracking in JSON data <http://variable-scope.com/posts/mutation-tracking-in-nested-json-structures-using-sqlalchemy>`_.
