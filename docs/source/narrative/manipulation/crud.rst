====
CRUD
====

Introduction
============

Websauna comes with :term:`CRUD`. CRUD is designed for :term:`SQLAlchemy models`, but can be storage mechanism agnostics and you can use with any arbitrary persistency mechanism. CRUD supports :ref:`form autogeneration`, so that a CRUD UI can be generated automatically for your model. CRUD is extensively used by :term:`admin`, but you can as well roll it standalone.

CRUD elements
=============

CRUD consists of basic views which are

* Listing view

* Add object

* Show object

* Edit object

* Delet object

CRUD controller is :ref:`traversal` based as thus can be plugged in to any part of the site without a hardcoded URL configuration.

You need do

* Declare one subclass of `websauna.system.crud.CRUD` which servers the entry point into your CRUD

* This class must contain inner class of subclass of `websauna.system.crud.CRUD.Resource` which wraps raw SQLAlchemy object to traversable URLs

After this you can override any of the views by subclassing the base view and customizing it for your purposes.

For example here is an URL from the tutorial::

    http://localhost:6543/admin/models/choice/zYkpKEkpSvq02tPjL_ko8Q/show

Below is how CRUD is formed. It consists of four :term:`resources <resource>`(see :py:class`websauna.system.core.traversal.Resource`) and one :term:`view`.

* ``admin`` is the default admin interface root of the site, see :py:class:`websauna.system.admin.admin.Admin`

* ``admin`` contains ``models`` path under which all CRUDs for models registered for admin are. This is presented by :py:class:`websauna.system.admin.modeladmin.ModelAdminRoot`

* ``choices`` is a CRUD root for Choices :term:`SQLAlchemy` :term:`model`. It is presented by ``myapp.admins.Choice`` which is a subclass of ``websauna.system.admin.modeladmin.ModelAdmin`` which in turn is subclass of :py:class:`websauna.system.crud.sqlalchemy.CRUD` which is the subclass of abstract CRUD implementation :py:class:`websauna.system.crud.CRUD`

* ``zYkpKEkpSvq02tPjL_ko8Q`` is the base64 encoded ::term:`UUID` (see :py:func:`websauna.system.utils.slug.uuid_to_slug`) of the ``myapp.admins.Choice`` we are currently manipulating. It resolves to ``myapp.admins.Choice.Resource`` class which is the subclass of :py:class:`websauna.system.crud.sqlachemy.Resource``. This resource wraps one SQLAlchemy object to URL traversing by giving it ``__parent__`` pointer and ``__name__`` string. URL to SQLAlchemy item mapping is done by :py:class:`websauna.system.crud.urlmapper.Base64UUIDMapper`.

* ``show`` is the :term:`view` name. Views are picked against the context they are registered. Here the context is ``myapp.admins.Choice.Resource``. It maps to :py:class:`websauna.system.admin.views.Show`, subclass of :py:class:`websauna.system.crud.views.Show`.

* View processing starts when Pyramid router calls :py:meth:`websauna.system.crud.views.Show.show`.

URL mapping
-----------

CRUD provides translation of SQLAlchemy object ids to URL paths and vice versa.

* :py:class:`websauna.system.crud.urlmapper.Base64UUIDMapper` is recommended as it generates non-guessable URLs. It reads :term:`UUID` attribute from model and constructs Base64 encoded string of it.

* :py:class:`websauna.system.crud.urlmapper.IdMapper` can be used if you want to have primary keys directly in URLs.

* The behavior can be configured by setting :py:attr:`websauna.system.crud.CRUD.mapper` for your CRUD class.

Form schema
-----------

CRUD supports

Listing view
============

TODO

Add view
========

TODO

Customizing created objects
---------------------------

Override ``create_object()``. Example:

.. code-block:: python

    @view_overrides(context=ReferralProgramAdmin)
    class ReferralProgramAdd(adminviews.Add):
        """Admin view for editing shortened URL."""

        # We only ask for name field, everything else is filled by system
        includes = [
            "name"
        ]

        def create_object(self):
            """When created through admin, all referral programs are internal type by default."""
            model = self.get_model()
            item = model()
            item.program_type = "internal"
            return item

Show view
=========

TODO

Edit view
=========

TODO

Delete view
===========

TODO

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


More info
=========

See :py:mod:`websauna.system.user.adminviews` for CRUD used in the user and groups admin.