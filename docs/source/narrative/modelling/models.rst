=======================
Interacting with models
=======================

Websauna models are based on SQLALchemy.

What are models and ORM?
========================

xxx

Creating models
===============

xxx

Interacting with model instances
================================

Creating item
-------------
xxx

Reading item
-------------

xxx

Updating item
-------------

Deleting item
-------------

By using query object
+++++++++++++++++++++

Example::

    User.query.filter_by(id=123).delete()

By using model instance
+++++++++++++++++++++++

Example::

    user = User.query.filter_by(id=123)
    dbsession.delete(user)



Indexes
=======

Full table scan
---------------

Situation when there is no index and the database needs to load every row of the table from the disk and process them to satisfy your query. Usually one wants to avoid this situation.

Btree
-----

Efficient random access.

BRIN
----

EFficient index for time series-like data where the field content doesn't change and written in the sorted order. For example you have ``created_at``.





More information
================

xxxx

