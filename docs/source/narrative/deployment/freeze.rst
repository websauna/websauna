==================================================
Pinning down application dependencies (pip freeze)
==================================================

Introduction
============

Before you can start deploying your application you first must freeze it Python package dependencies. Freezing is a proces where :term:`pip` reads the versions of all installed packages in a local virtual environment and then produces a ``requirements.txt`` out of them.

How to perform a freeze
=======================

In your application package root folder do::

.. code-block:: console

    pip freeze > requirements.txt

If your virtual environment is polluted and you have not kept one virtual environment per project it is suggested to create a new virtual environment from the scratch and run ``pip install -e .``.

Edit ``requirements.txt`` and remove the line which refers your own project (``myapp`` in this case)::

    -e git+git@bitbucket.org:miohtama/myapp.git@fa8f22c25a8cdfa1d151f61b54b2c8ed8c35defd#egg=myapp

Then commit this file.

What happens without freezing?
==============================

New Python package versions are released every day. Sooner or later one of your dependency projects will release a version which is not compatible with the API your application expects it to have. Because ``pip`` command installs latest versions by default, it would install an incompatible package version for your application. This would cause your application to crash or not to start.

``requirements.txt`` maintains the list of absolute version numbers. When pip uses it to fetch the packages, it always gets the same version you had when developing the application, not possible incompatible latest version.

Advanced
========

Tracking Websauna master
------------------------

If you need to run your application against Websauna master (or any Git revision) you can edit ``websauna`` dependency in ``requirements.txt``::

    -e git+git@github.com:websauna/websauna.git@master#egg=websauna

More information
================

`Declaring dependencies in Python <http://blog.ziade.org/2013/04/13/declaring-dependencies-in-python/>`_.

