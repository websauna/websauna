=========
Traversal
=========

Websauna supports traversal pattern to map out resource trees to URLs. It is extensively used by the default :term:`CRUD` and :term:`admin` interfaces.

Websauna traversal is based on `Pyramid traversal architecture <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html>`_.

Resources
=========

An object representing a node in the resource tree of an application. If traversal is used, a resource is an element in the resource tree traversed by the system. When traversal is used, a resource becomes the context of a view.

Websauna provides :py:class:`websauna.system.core.traversal.Resource` base class from which you can inherit all resource classes. The API documentation explains how to set up resource objects.

Breadcrumbs
===========

It's very easy to generate breadcrumbs (path bar) from traversal hierarchy. See :py:mod:`websauna.system.core.breadcrumbs` for more information.

More information
================

`Traversal in Pyramid documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html>`_.
