


pyramid_web20.superuser
-----------------------

List of superuser emails or usernames. Add your username on this list to make it super user.

Example::

    pyramid_web20.superuser =
        admin
        mikko@example.com

.. warning::

    Superuser permission allows executing arbitrary code on the server.


pyramid_web20.global_config
---------------------------

This is a reference to ``global_config`` object which is used to initialize Pyramid application. It is a dictionary. Example::

    {'__file__': '/Users/mikko/code/trees/trees/development.ini', 'here': '/Users/mikko/code/trees/trees'}