=========
Templates
=========

Introduction
============

Websauna uses Jinja 2 template language in its default templates. You are, however, free to choose any other template engine for your templates (see Pyramid template support).

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
