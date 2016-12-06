=========
Traversal
=========

.. contents:: :local:

Introduction
============

Websauna supports traversal pattern to map out resource trees to URLs. It is extensively used by the default :term:`CRUD` and :term:`admin` interfaces.

Websauna traversal is based on `Pyramid traversal architecture <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html>`_.

.. _resource:

Resources
=========

An object representing a node in the resource tree of an application. If traversal is used, a resource is an element in the resource tree traversed by the system. When traversal is used, a resource becomes the context of a view.

Websauna provides :py:class:`websauna.system.core.traversal.Resource` base class from which you can inherit all resource classes. The API documentation explains how to set up resource objects.

Resource publicity
------------------

The default Websauna Root object declares all traverable content to be public. If you need to make your resources private see :ref:`make-resource-private`.

Breadcrumbs
===========

It's very easy to generate breadcrumbs (path bar) from traversal hierarchy. See :py:mod:`websauna.system.core.breadcrumbs` for more information.

Examples
========

See `websauna.blog.views <https://github.com/websauna/websauna.blog/blob/master/websauna/blog/views.py>`_ module for example how to set up a traversal for your frontend pages.


Site root object
================

Websauna provides a :py:class:`websauna.system.core.root.Root` class that is the default root object for traversal. This object defines user and group permissions on the site level.

You can override this object in :py:meth:`websauna.system.Initializer.configure_root`.

Example ``root.py``:

.. code-block:: python

    from pyramid.security import Allow
    from websauna.system.core import root as base


    class Root(base.Root):
        """Redefine site root permissions."""

        # Additional site specific permissions given to the admin group
        __acl__ = [
            (Allow, "group:admin", "manage-content")
        ]

        # Default websauna permissions
        __acl__ += base.Root.__acl__

Example ``__init__.py``:

.. code-block:: python

    class Initializer(websauna.system.Initializer):

        def configure_root(self):
            from myapp.root import Root
            self.config.set_root_factory(Root.root_factory)

More information
================

`Traversal in Pyramid documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html>`_.
