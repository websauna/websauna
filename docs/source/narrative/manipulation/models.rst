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
+++++++++++++
xxx

Reading item
++++++++++++

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

More information
================

xxxx
