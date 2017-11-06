===================
JSON data in models
===================

.. contents:: :local:

Introduction
============

JSON data storage is ideal when you do not know all the schema key or columns beforehand.

* You are iterating early versions of your data models and do not know how they end up look like

* You are storing data from an external source like a third party API giving JSON return values

:term:`PostgreSQL` database offers very powerful :term:`JSONB` column that store schemaless :term:`JSON`-like data directly in :term:`SQL` database. This gives many advantages of NoSQL-like data processing, but by still maintaining high :term:`ACID` guarantees given by PostgreSQL.

For SQLite Websauna offers a fallback in :py:class:`websauna.system.model.columns.JSONB`.

Using JSONB column
==================

You need to wrap JSON/JSONB column types with a :py:func:`NestedMutationDict.as_mutable` function that enables deep mutated state tracking for SQLAlchemy. This means that SQLAlchemy objects are properly committed when you change dictionary keys or list items and you do not manually need to call SQLAlchemy's ``mark_dirty`` function.

Here is an example how to declare a basic column containg JSONB data and how to use it:

.. code-block:: python

    import sqlalchemy as sa
    import sqlalchemy.orm as orm
    from sqlalchemy.orm import Session
    from websauna.system.model.columns import UTCDateTime

    from websauna.system.model.meta import Base
    from websauna.system.user.models import User
    from websauna.utils.time import now
    from websauna.system.model.json import NestedMutationDict
    from websauna.system.model.columns import JSONB


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

    # Mutation tracking for an object that has not been added to a session yet
    v = Verification()
    v.verification_data["name"] = "Mikko Ohtamaa"
    v.verification_data["hometown"] = "Toholampi"
    dbsession.add(v)
    transaction.commit()

    # Mutation tracking for an object that has been committed and is in active session,
    # but not dirty
    v.verification_data["hometown"] = "Toholampi"

    # Mutation tracking for an object that is loaded from the database
    v = dbsession.query(Verification).first()
    for key, value in v.verification_data.items():
        print("{} is {}".format(key, value))

You can also update dictionary data directly from an external source, like API call returning JSON data:

.. code-block:: python

    source_data = {"car": "DeLorean", "color": "red"}
    v = Verification()
    v.verification_data.update(source_data)

Default values
==============

JSON columns can take default values as form of ``None``, empty ``dict`` or ``list`` or prefilled dicts.

Default values are converted to :py:class:`websauna.system.model.json.NestedMixin` instances under the hood. This is done by decorating the classes with :py:func:`websauna.system.model.json.init_for_json` when you use Websauna ``Base`` model or :py:func:`websauna.system.model.utils.attach_model_to_base` helper. The connection is made through SQLAlchemy events.

.. note::

    By SQLAlchemy rules, the default data is not available to modify/read until you have called ``dbsession.flush``.

Example.

.. code-block:: python

    import sqlalchemy as sa
    import sqlalchemy.orm as orm

    from websauna.system.model.meta import Base
    from websauna.system.user.models import User
    from websauna.utils.time import now
    from websauna.system.model.json import NestedMutationDict
    from websauna.system.model.columns import JSONB


    #: Initialze user_data JSONB structure with these fields on new User
    DEFAULT_USER_DATA = {
        "full_name": None,

        # The initial sign up method (email, phone no, imported, Facebook) for this user
        "registration_source": None,

        # Is it the first time this user is logging to our system? If it is then take the user to fill in the profile page.
        "first_login": True,

        "social": {
            # Each of the social media login data imported here as it goes through SocialLoginMapper.import_social_media_user()
        }
    }


    class User(Base):

        #: Misc. user data as a bag of JSON. Do not access directly, but use JSONBProperties below
        user_data = sa.Column(NestedMutationDict.as_mutable(JSONB), default=DEFAULT_USER_DATA)


    # Then ...

    u = User()
    dbsession.add(u)
    dbsession.flush()
    print(u.user_data["first_login"])  # True

Nested mutation tracking
========================

:py:class:`websauna.system.model.json.NestedMutationDict` provides nested state tracking for JSON column dictionaries.

This means that the following works:

.. code-block:: python

    v = Verification()
    v.verification_data["name"] = "Mikko Ohtamaa"
    v.verification_data["subdata"] = {}
    dbsession.add(v)
    transaction.commit()

    v = dbsession.query(Verification).first()
    # Plain SQLAlchemy JSONB would not mark v object
    # dirty when we set a dictionary key here.
    # The change would not be stored in the following commit
    v.verification_data["subdata"]["subitem"] = "+1 505 123 1234"
    transaction.commit()


For more information see :py:mod:`websauna.system.model.json`.

Indexed properties
==================

SQLAlchemy offers :py:func:`sqlalchemy.ext.indexable.index_property` descriptor that can be used to short cut data access inside a JSON dictionary.

Example:

.. code-block:: python

    from sqlalchemy.ext.indexable import index_property

    #: Initialze user_data JSONB structure with these fields on new User
    DEFAULT_USER_DATA = {

        # The initial sign up method (email, phone no, imported, Facebook) for this user
        "registration_source": None,

    }

    class UserMixin:


        #: Misc. user data as a bag of JSON. Do not access directly, but use JSONBProperties below
        user_data = Column(NestedMutationDict.as_mutable(JSONB), default=DEFAULT_USER_DATA)

        #: How this user signed up to the site. May include string like "email", "facebook" or "dummy". Up to the application to use this field. Default social media logins and email sign up set this.
        registration_source = index_property("user_data", "registration_source")


    # Now you can do

    u = User()
    dbsession.add(u)
    dbsession.flush()
    print(u.registration_source)

Non-JSON serializable types
===========================

By default the following Python data does not serialize as JSON:

* :py:class:`decimal.Decimal`

* :py:class:`datetime.datetime`

* :py:class:`uuid.UUID`

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
