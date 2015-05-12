
Template variables
==================

The following variables are available in the templates, as set by :py:mod:`pyramid_web20.system.core.templatecontext`.

Other template context
======================

Permission checks
-----------------

Use :py:meth:`pyramid.request.Request.has_permission` to check if the user has the named permission in the current context.

Site root context
------------------

Use :py:meth:`pyramid.request.Request.root`.

