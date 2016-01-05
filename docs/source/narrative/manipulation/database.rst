==============
Using database
==============

SQL database
============

Websaunan uses an SQL database. SQLAlchemy object relations mapping (ORM) library is used to create Python classes representing the model of data. From these models corresponding SQL database tables are created in the database.

By default, PostgreSQL database software is recommended, though Websauna should be compatible with all databases supported by SQLAlchemy

Accessing database session
--------------------------

All database operations are done through SQLAlchemy session.

Session in a HTTP request
+++++++++++++++++++++++++

Session in a command line application
+++++++++++++++++++++++++++++++++++++

You can get a access to the database session through a :py:class:`websauna.system.Initializer` instance exposed through a constructed WSGI application::



Session in a task
+++++++++++++++++

asas