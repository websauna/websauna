Indexes
=======

How to make indexes for your SQL data for more efficient access.

TODO

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

