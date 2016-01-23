=====
Admin
=====

.. contents:: :local:

Introduction
============

Admin, or administration interface, provides super administrator capabilities for your Websauna site. You can easily browse, add and edit data without need to write explicit forms and views or install additional software for database browsing.

Admin is accessible for users who belong *admin* group. The first signed up user is automatically added to this group. Different permissions schemes can be implemented through :term:`ACL`, so that groups of people can only view partial data or cannot modify it.

Admin is automatically generated for your data :doc:`models <./models>`_. It is based on Websauna :doc:`CRUD <./crud>` and :doc:`automatic form generation <../form/autoform>`.

Admin URL breakdown
===================

Below is a sample breakdown of admin traversal of one item.

Creating an admin view
======================

Below is instructions how to create your own admin views. We use a view called *phone order* as an example.

Create a Pyramid traversal view and register it against Admin context. First we create a stub ``phoneorder.py``::

    from pyramid.view import view_config

    from websauna.system.admin import Admin

    @view_config(context=Admin, name="phone-order", route_name="admin", permission="edit", renderer="admin/phone_order.html")
    def phone_order(context, request):
        return {}

In your Initializer make sure the module where you view lies is scanned::

    class Initializer:

        ...

        def config_admin(self):
            super(Initializer, self).config_admin()
            from . import phoneorder
            self.config.scan(phoneorder)

In the template ``phone_order.html``::

    {% extends "admin/base.html" %}

    {% block admin_content %}
    <p>Content goes here...</p>
    {% endblock %}


Then you can later get the link to this page in template code::

    <p>
        <a href="{{ request.resource_url(admin, 'phone-order') }}>Create phone order</a>
    </p>

Getting an model instance link in admin
=======================================

Preface: You have an SQLAlchemy object and you want to provide the link to its admin interface: show, edit or custom action.

To construct a link to the model instance inside admin interface, you need to

* Get a hold of the current admin object

* Ask admin to provide traversable resource for this object

* Use ``request.resource_url()`` to get the link

Example::

    # Get admin singleton from the registry
    admin = Admin.get_admin(request.registry)

    # Get traversable resource for a model instance
    resource = admin.get_admin_resource(user)

    # Get a context view named "edit" for this resource
    edit_link = request.resource_url(resource, "edit")
