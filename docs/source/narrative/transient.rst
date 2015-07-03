==============
Transient data
==============

Introduction
============

In the context of Websauna transient data means data

* Which might not be around forever

* Might be cache-like data

* Might be user session data

* Is optimized for speed instead of persistence

* Might not be tied to normal database transaction lifecycle

* Might not have complex query properties like SQL, but is more key-value like

The stack component for managing transient data in Websauna is Redis.

Introduction to Redis
=====================

TODO

Managing Redis database
=======================

* Use ``redis-cli`` tool or Python shell to explore the contents of Redis database

* The default backup script dumps Redis database for backing up