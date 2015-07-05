====
CRUD
====

Introduction
============

CRUD stands for create-read-update-delete. It's the basic usage pattern in every web application dealing with any data. You add data, you come later to edit it. In the context of Websauna, CRUD is the abstract subsystem used to generate forms.

CRUD forms the base of the model admin user interface, but it can be used standalone. For example, you can create user specific listings under user profile e.g. "My purchases".

Websauna CRUD is designed to be storage mechanism agnostics - it works with SQLAlchemy models, as well as with Redis, or anything you feed for it.

Putting together CRUD
=====================

Here is an example how to put together a simple CRUD.

Object id mapping
=================

CRUD provides translation of object ids to URL paths and vice versa.

* You can use integer primary key numbers as the object ids

* You can use UUIDs for sensitive data

This is handled by settings the mapper attribute of CRUD.

Resource buttons
================

One part of the CRUD view is resource buttons which allows jumping between different CRUD views.

TODO: Screenshot here

You can add these buttons yourself. Example:

.. code-block:: python

    from websauna.viewconfig import view_overrides
    from websauna.system.crud.views import TraverseLinkButton
    from websauna.system.user import adminviews as useradminviews

    from yourproject.admin import UserAdmin

    @view_overrides(context=admin.UserAdmin.Resource)
    class UserShow(useradminviews.UserShow):
        """View for displaying user information in admin."""

        # Add two more actions for the users
        resource_buttons = [

            # Default edit action
            TraverseLinkButton(id="edit", name="Edit", view_name="edit"),

            # New custom actions
            TraverseLinkButton(id="sms-user", name="Send SMS", view_name="sms-user"),
            TraverseLinkButton(id="license", name="Medical license", view_name="license")
        ]
