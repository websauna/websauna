==========================
JSON fields and properties
==========================

Introduction
============

:term:`PostgreSQL` database offers very powerful :term:`JSONB` column which allows store schemaless data easily based on :term:`JSON`. This gives many advantages of "NoSQL"-like databases by still maintaining :term`ACID` guarantees.

Websauna takes advantage of this and offers integration glue over what :term:`SQLAlchemy` offers by default.

Using JSONB column
==================

See :py:class:`sqlalchemy.dialects.postgresql.JSONB`.

Default usage
-------------

:py:class:`websauna.system.user.usermixin.UserMixin` provides example in the format of ``user_data`` where random user variables and all social media connected data is stored.

Using JSONBProperty
===================

Use cases

* No migration needed when adding new properties

* You can refer inside non-structured data you have dumped on JSON column from external source

* Mutation tracking

JSON serialization issues
-------------------------

By default Python's ``Decimal`` or ``datetime`` objects do not serialize as JSON.

More information
================

`Automatic mutation tracking in JSON data <http://variable-scope.com/posts/mutation-tracking-in-nested-json-structures-using-sqlalchemy>`_.