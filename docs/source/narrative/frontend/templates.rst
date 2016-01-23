=========
Templates
=========

Introduction
============

Websauna uses :term:`Jinja` 2 template language in its default templates. You are free to choose any other template engine for your templates. See :term:`Pyramid` support for `different template engines <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/templates.html#available-add-on-template-system-bindings>`_.

Template reference
==================

See :doc:`template reference <../../reference/templates>` to get yourself familiar with core templates.

Rendering a template
====================

View use case
-------------

The template is usually rendered by returning a template context dictionary from a view function. The template context dictionary is passed to a template defined by ``renderer`` parameter in the view config. ``renderer`` must be a path to a file defined in one of the template paths.

Manual rendering
----------------

You can manually render a template by calling ``pyramid.renderers.render``. Example::

    from pyramid.renderers import render

    def my_utility_function(request, first_name, last_name):
        output = render("hello_world.txt", dict(first_name=first_name, last_name=last_name), request=request)

Alternatively if you know the output will be a HTTP response you can use ``pyramid.renderers.render_to_response``::

    from pyramid.renderers import render_to_response

    def my_view(request):
        return render_to_response("hello_world.html", dict(first_name="Mikko", last_name="Ohtamaa"), request=request)

Defining template paths
-----------------------

TODO

Linking
=======

Traversing links
----------------

If you have a traversable object and want to build a link for it

* First get a handle of corresponding traversing Resource object

* Then call ``request.resource_url()`` or use template ``model_url`` filter to build a link

* Admin object has a helper function ``get_admin_resource()`` to get a ``Resource`` of any SQLAlchemy instance managed in the model admin

Example how to build a link to the ``customer`` user instance in a ``delivery`` template context variable. The view name is ``sms-user``:

.. code-block:: html

    <a href="{{ admin.get_admin_resource(delivery.customer)|model_url('sms-user') }}" id="btn-sms-user" class="btn btn-default">
        Send SMS to customer
    </a>

The actual view definition looks like:

.. code-block:: python

    @view_config(context=admin.UserAdmin.Resource, name="sms-user", route_name="admin", permission='edit', renderer="admin/sms_user.html")
    def sms_user(context, request):
        user = context.get_object()
        # ...
